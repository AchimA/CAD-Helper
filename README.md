# Blender Extension: CAD Helper

> [!NOTE] TEST\
> This "add-on" has now been ported to a modern Blender "extension".\
> To install / update it, please use **Edit > Preferences > Get Extensions** and search for **CAD-Helper**.

Blender Extension for imported CAD assemblies.
<img src="images/ui-panel.png" alt="User Interface" width="300"/>


## Functions:
Ths extension aims to simplyfy the cleaning & restructuring of imported CAD assemblies. This is especially helpful for largre assemblies with hundreds of parts and many nested sub-assemblies.

Mosts operators work on selections (either one or multiple objects within the assembly structure).

Implemented operators are: 
* **Selection Helper**
    * Select parent or child objects (with or without extending the selection)
    * Recursivley select all child elements of the current selection
* **Selection Filtering**
    * Filter the selection by their name (simple string match & RegEx)^.
    * Filter the selection by object type (EMPTY, MESH, CURVE, etc.)
    * Filter the selection by bounding box size.Lets you specifiy a min and max size in % relative to the selected parts.
    * Filter the selection by vertex count.
* **Clean-Up**
    * Delete one or multiple objects in the hirarchy. All the children of the selected objects are automatically reconnected to their 'grand-parents' before they are deleted.
    * Delete all leafes empties (empties without children) below the selected objects.
    * Flattens the hierarchy below any selected nodes.
    * Flattens the hierarchy below any selected nodes and joins all the mesh objects. All modifiers are applied before joining.
    * Set the object (part) origins relative to the part geometry
    * Resize all the selected empties, without resizing all of the children
    * Set the empty (assembly origin) position to the average of all the child objects.
* **Origins**
    * Sets the origin of mesh objects to their bounding box center.
* **Empties**
    * Normalize the size of the selected empties.
    * Place the empties at the center (median) of the location of its children.
* **Transfer Material Properties [:exclamation: Experimental]**
    * Transfer material properties between Principled BSDF Node and View Port Display settings.
    This is sometimes required as some CAD export color, roughness & alpha to the View Port Display instead of the actual material node (i.e. BIM).
* **Clean-Up Materials  [:exclamation: Experimental]**
    * Clear viewport colors. Resets all objects to standard gray, when viewd in solid shading
    * Clear all materials from selected objects
    * Remove duplicated materials.
    This compares base color, alpha, roughness and metallic in the BSDF node and replaces all materials with the same values.\
    :information_source: This operator works on the entire scene, not only selected objects.
* **Link / Object-Data Helper  [:exclamation: Experimental]**
    * Detect same-named object groups (e.g., exported duplicates like screws) and link their mesh data. This can greatly reduce the number of vertices.
    :exclamation: Since only the name is checked, it might have unwanted behalviour. Please be shure to check the outcome! :exclamation:

# Installation:

1. Download the *.zip file of the latest release onto your hard-drive: 
https://github.com/AchimA/CAD-Helper/releases/latest/download/CAD-Helper.zip
1. In Blender
    1. Got to Edit / Preferences / Add-ons
    1. Hit install and select the downloaded *.zip file
    1. Activate the addon by ticking the box
1. The add-on can then be accessed in the 3D view right side-bar (N-menu).