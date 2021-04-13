---
template: post.html
author: Karthik D
author_dp: /assets/dp2.png
title: Loading a large json file into elixir's ETS (Erlang Term Storage) Cache using Jaxon
url: /how-to-load-a-large-json-file-into-elixir-ets-cache
cover: /assets/code.jpg
published_date: 2021-04-13T09:00:00+05:30
modified_date: 2021-04-13T09:00:00+05:30
display_date: 13 April, 2021
---
Elixir's ETS cache is an in-memory data store that can be accessed across processes. It can be used to build lookup tables such as geocoders, translators etc. in web applications.

For an application I was building, I had to load a large dataset (~500k rows) of geocodes into an ETS table before the webserver endpoint starts. This data can be shared across all the processes that handle incoming requests.

## First attempt: Load the file and then parse
At first, I attempted loading the file into memory, then parsing it with Jason and...
```
# here my json is one single root object with key-value pairs
def load_file(filename, tablename) do      
  :ets.new(tablename, [:named_table])
  with {:ok, body} <- File.read(filename), {:ok, json} <- Jason.decode(body),
  do: load_from_map(json, tablename)
end

defp load_from_map(parsed_map, tablename) do
  :ets.new(tablename, [:named_table])
  for {k,v} <- parsed_map do
    :ets.insert(tablename, {k,v})
  end
end              
```
It worked, but it took quite a while and hogged quite some RAM. My machine with 4GB RAM froze for about a minute.

## Streaming to the rescue
At this point, I thought there could be a better way to do this, may be something that doesn't involve reading the entire file into memory. That's when I found [Jaxon](https://github.com/boudra/jaxon), a streaming JSON Parser. So now the file is opened as a stream and the JSON is parsed as the stream is being read. Pretty neat right?
```
# here my json is an array of objects {"k":<key>,"v":<value>}
def load_file(filename, tablename) do      
  :ets.new(tablename, [:named_table])
  filename
  |> File.stream!()
  |> Jaxon.Stream.from_enumerable()
  |> Jaxon.Stream.query([:root, :all])
  |> Stream.each(fn (kv) -> :ets.insert(tablename, {kv["k"],kv["v"]}) end)
  |> Stream.run()
end
```

At first this didn't seem to work and I was disappointed until I realized I my JSON wasn't pretty and was just a single line. I generated a multi-line pretty JSON and voila! It worked!
