# Blender Addon: CAD Helper
Blender Addon for imported CAD assemblies.

<img src="images/ui-panel.png" alt="User Interface" width="300"/>

## Functions:

In a hierarchical CAD model (with sub-assemblies and parts), select one or more of the objects. You can then:
* **Selection Helper**
    * Select parent or child objects (with or without extending the selection)
    * Recursivley select all child elements of the current selection
* **Selection Filtering**
    * Allows to filter all the selected parts by bounding box size.Lets you specifiy a min and max size in % relative to the selected parts.
    * Allows to filter all the selected parts by object type (EMPTY, MESH, CURVE, etc.)
    * Allows to filter all the selected parts by their name (simple string match & RegEx)
* **Clean-Up**
    * Delete one or multiple objects in the hirarchy. All the children of the selected objects are automatically reconnected to their 'grand-parents' before they are deleted.
    * Below the selected object(s); all leafes empties (empties without children) are deleted.
    * Flatten the hierarchy below any selected nodes
    * Flatten the hierarchy below any selected nodes and joins all the mesh objects. All modifiers are applied before joining.
    * Set the object (part) origins relative to the part geometry
    * Resize all the selected empties, without resizing all of the children
    * Set the empty (assembly origin) position to the average of all the child objects
* **Transfer Material Properties**
    * Transfer material properties between Principled BSDF Node and View Port Display settings.
    This is sometimes required as some CAD export color, roughness & alpha to the View Port Display instead of the actual material node (i.e. BIM)
* **Clean-Up Materials**
    * Clear viewport colors. Resets all objects to standard gray, when viewd in solid shading
    * Clear all materials from selected objects
    * Remove duplicated materials.
    This compares base color, alpha, roughness and metallic in the BSDF node and replaces all materials with the same values. This operator works on the entire scene, not only selected objects.


# Installation:

1. Download the *.zip file of the latest release onto your hard-drive: 
https://github.com/AchimA/CAD-Helper/releases/latest/download/CAD-Helper.zip
1. In Blender
    1. Got to Edit / Preferences / Add-ons
    1. Hit install and select the downloaded *.zip file
    1. Activate the addon by ticking the box
1. The add-on can then be accessed in the 3D view right side-bar (N-menu).