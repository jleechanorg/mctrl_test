alias SymphonyElixir.Linear.Issue

node_name = System.fetch_env!("SYMPHONY_DAEMON_NODE")
cookie = System.fetch_env!("SYMPHONY_DAEMON_COOKIE")
issues_json_path = System.fetch_env!("TASK_ISSUES_JSON")

sender_node = String.to_atom("enqueue_#{System.unique_integer([:positive])}")
{:ok, _} = Node.start(sender_node, :shortnames)
Node.set_cookie(String.to_atom(cookie))

resolved_node_name =
  if String.contains?(node_name, "@") do
    node_name
  else
    {:ok, host} = :inet.gethostname()

    host_short =
      host
      |> to_string()
      |> String.split(".", parts: 2)
      |> hd()

    "#{node_name}@#{host_short}"
  end

target_node = String.to_atom(resolved_node_name)

connect_ok? =
  1..20
  |> Enum.any?(fn _attempt ->
    if Node.connect(target_node) do
      true
    else
      Process.sleep(250)
      false
    end
  end)

if not connect_ok? do
  IO.puts(:stderr, "failed_to_connect node=#{resolved_node_name}")
  System.halt(1)
end

issues_payload =
  issues_json_path
  |> File.read!()
  |> Jason.decode!()

incoming_issues =
  Enum.map(issues_payload["issues"], fn item ->
    %Issue{
      id: item["id"],
      identifier: item["identifier"],
      title: item["title"],
      state: item["state"] || "Todo",
      description: item["description"] || "",
      labels: item["labels"] || [],
      assigned_to_worker: item["assigned_to_worker"] || true
    }
  end)

existing_issues =
  case :rpc.call(target_node, Application, :get_env, [:symphony_elixir, :memory_tracker_issues, []]) do
    issues when is_list(issues) -> Enum.filter(issues, &match?(%Issue{}, &1))
    _ -> []
  end

merged_by_id =
  (existing_issues ++ incoming_issues)
  |> Enum.reduce(%{}, fn issue, acc -> Map.put(acc, issue.id, issue) end)

merged_issues = Map.values(merged_by_id)

:ok =
  :rpc.call(target_node, Application, :put_env, [
    :symphony_elixir,
    :memory_tracker_issues,
    merged_issues
  ])

IO.puts("enqueued=#{length(incoming_issues)}")
IO.puts("total_queue=#{length(merged_issues)}")

for issue <- incoming_issues do
  IO.puts("issue=#{issue.identifier}\ttitle=#{issue.title}")
end
