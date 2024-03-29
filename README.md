# `polkadot` - Data Flow Diagrams for Faithless Developers

## What is `polkadot`

`polkadot` is a new specification for data flow diagrams. Think of it as blueprints for developers. Construction workers can show you the different parts of what they are working on (built or planned). Likewise, a `polkadot` diagram should allow you to point your finger at a particular component and say: this is where I spent my time today.

`polkadot` digrams should be used as "maps" of software systems. Just like real-world maps, One must understand that
[the map](https://en.wikipedia.org/wiki/Map%E2%80%93territory_relation) 
[is not](https://en.wikipedia.org/wiki/The_Map_and_the_Territory) 
[the territory](https://en.wikipedia.org/wiki/On_Exactitude_in_Science). By that I mean - not everything on the system will be represented on the diagram. When you read or write a diagram, it represents your view of what is and what is not important for understanding the system as a whole. On the other hand - everything added to the diagram should appear in the actual system, and with an exact-as-possible reference to its whereabouts so that you can locate and validate it's really there, doing what the diagram claims it is capable of doing.

Like [Markdown](https://en.wikipedia.org/wiki/Markdown), `polkadot` is text-based, concise, easy to learn and might have [different tastes in different places](https://en.wikipedia.org/wiki/Markdown#Variants). My hope is that once people (mostly developers) will grok `polkadot`, it will become the de-facto way to communicate ideas.

While you can choose any diagram tool, my examples would be in my favourite diagramming language which is `dot` - hence the project's name.

[Simple Made Easy](https://www.infoq.com/presentations/Simple-Made-Easy/) 
by Rich Hickey (creator of the Clojure programming language).

[Nothing is Something](https://www.youtube.com/watch?v=OMPfEXIlTVE) by Sandi Metz (programmer and author).


## `dot` used in `polkadot`

* digraph
* subgraph
* node
* subgraph cluster_
  * label
  * labeljust 
* shapes: box & square, cylinder, box3d, ellipse & circle, note

## Target Audience

* Developers and Software Engineers, in particular Data Engineers and Machine Learning Engineers.
* Visual thinkers. People who would prefer a diagram in addition to the written documentation.
* People suffering from attention deficit disorders (such as myself). I find diagrams, and in particular graphs, help me focus on a single node and its neighbors. It helps me fit things in my [7±2 working memory capacity ](https://en.wikipedia.org/wiki/The_Magical_Number_Seven,_Plus_or_Minus_Two) and not get lost.
* Python developers, in particular on OS X / Linux. While `polkadot` is an idea, all tooling will be initially implemented in Python, as this is my core language. I hope that if others will like it, additional implementations would become available.


## What `polkadot` isn't

* A new programming language/DSL.
* A UML replacement; UML is too complex to learn (I know: I taught it to MSc students for 2 years!), while `polkadot` should be swift to learn.
* A tool suitable for describing any software system: in my career I am most concerned with systems for transforming data, in particular for the sake of Machine Learning pipelines. I'm not sure game developers (for example) will find `polkadot` useful, nor am I worried about this `:)` .


## Editors

(OS X only, send me your favourites from other platforms and I'll add them!)

* **DOT:** [Graph Galaxy](https://apps.apple.com/us/app/graph-galaxy/id1473722262?mt=12). Really low reviews but I actually like it a lot!
* **Mermaid.js:** [iemanja](https://github.com/pedsm/iemanja/releases). First editor I found on Google, looks good to me `:)`
* **Code:** [Sublime Text](https://www.sublimetext.com/). The only editor I keep paying for out of my own pocket. Love it.
* **Markdown:** [MacDown](https://macdown.uranusjr.com/). When you want to focus on writing (as I do right now!).
* **UML:** [PlantUML](https://plantuml.com/). For those who still miss good ol' UML.
* **Python:** [black](https://github.com/psf/black). It's not an editor, just my favourite formatter.
A project is a directory that contains:

* A `.dot` or `.gv` for the graph.
* For each programming language, its respective imports script/code.

The perfect world/machine is doing all locally, single-thread, no concurrency, no space/time/cost limit.

Let's do it with `golang`.

```
polkadot
	png
	svg
	expand / unroll
	v | validate / c | check / e | evaluate
```	

Templates for each language!!!

validate:

1. Show bindings (and languages)
2. Show what's left to bind.
3. Show the graph goes by the rules!

# The Rules



	