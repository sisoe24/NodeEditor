# README

A work in progress project to create a scripting framework in Python by using a nodal approach built in PySide2.

Watch [demo](#demo)

## Description

My goal for this project is to create a visual scripting API for Python.
Alternatively, one could also use it in software that implements PyQt/PySide and
generate a scripting framework much like the Blueprint system in Unreal Engine.

Essentially a convenient way to program without writing code, 
handy for technical artists who have less time to dive into coding mastery.

## Why

It is a mix of a case study of more complex components of PySide and the challenge
of creating a visual scripting language, which is a noteworthy endeavor by itself 
since it has always been my dream for a long time after discovering the Blueprint system of UE.

## Install

The project uses `poetry` as the package manager:

```sh
poetry install
poetry run python -m src.main
```

## Usage

**Note** Currently the project is in a very limited state.

- You can create nodes via the Toolbar, Menu Bar or right click context menu.
- You can connect nodes by left dragging an edge from an output socket.
- You can load, save files.
- You can execute some of the nodes which are part of the execution flow.

## Create a custom node

There is a script inside the scripts folder `create_node.py` that will create a custom
node template. Upon starting, the script will ask for the node class name and the node name, 
which can be anything. Once created, the script will create a new file inside `src/nodes/classes` with the new node.

The node will start as a blanket template, i.e., no sockets.

The node is subdivided into two sections: The Node class and the Node content.
The node content is where you would put the node's logic with its appropriate sockets.

For now, I suggest looking at other nodes inside the `nodes/classes` folder to see how they work. 
Ideally, it should be documented, but I don't think it is appropriate at this stage since much of the code is likely to change.

## Notes

- Although the core logic is there, the project is not exactly in a working state.
  I am still trying to figure out most of the nodes with their execution, and there are many bugs and unfinished features.
- I want to give merit to [Pavel Křupala](https://gitlab.com/pavel.krupala) for inspiring me to start this project.

## Demo

![demo](resources/demo.gif)
