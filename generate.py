import mistune

mdparser = mistune.Markdown()
template = ""
md = ""

with open("index.html.template") as f:
  template = f.read()
  f.close()

with open("README.md") as f:
  md = f.read()
  f.close()

html = mdparser(md)
  
with open("index.html","w") as f:
  f.write(template.replace("{{htmlgoeshere}}",html))
  f.close()
  
