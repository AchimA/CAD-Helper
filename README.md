> **NOTE:** This "add-on" has now been ported to a modern Blender "extension". To install / update it, please use **Edit > Preferences > Get Extensions** and search for **CAD-Helper**.\
> https://extensions.blender.org/add-ons/cad-helper/



# <img src="images/ICON.png" alt="Icon" width="86"/> Blender Extension: CAD Helper


Blender Extension for imported CAD assemblies.\
<img src="images/CAD-Helper_0.6.3.png" alt="User Interface" width="100%"/>

## Functions:
This extension aims to simplify the cleaning & restructuring of imported CAD assemblies. This is especially helpful for larger assemblies with hundreds of parts and many nested sub-assemblies.

Most operators work on selections (either one or multiple objects within the assembly structure).

Implemented operators are: 
* **Hierarchy Selection**
    * Select parent or child objects (with or without extending the selection)
    * Recursively select all child elements of the current selection
* **Selection Filtering**
    * Filter the selection by their name (simple string match & RegEx).
    * Filter the selection by object type (EMPTY, MESH, CURVE, etc.)
* **Visualisation & Selection**
    * Filter and select by: Poly. Count, Hierarchy Depth & Bounding Box Size
* **Clean-Up**
    * Delete one or multiple objects in the hierarchy. All the children of the selected objects are automatically reconnected to their 'grand-parents' before they are deleted.
    * Delete all leaf empties (empties without children) below the selected objects.
    * Flattens the hierarchy below any selected nodes.
    * Flattens the hierarchy below any selected nodes and joins all the mesh objects. All modifiers are applied before joining.
    * Resize all the selected empties, without resizing all of the children
    * Set the empty (assembly origin) position to the average of all the child objects.
* **Instance Detection & Linking**
    * Detect identical objects by grouping them by vertex count, face area, bounding box axes length, bounding box volume. The detected groups can then be linked, such that they share the same mesh data-block.  
    ❗→ This might have unwanted behaviour, since false positives could occur. Please be sure to check the outcome!

**Tip:**
Use FreeCAD to convert \*.STEP files to \*.glb.

## Showcase

[![CAD-Helper Functions Demo](images/CAD-Helper_0.6.3.png)](images/CAD-Helper_0.6.3.mp4)

If the embedded preview does not play on your platform, open the video directly:
[Watch CAD-Helper demo video](images/CAD-Helper_0.6.3.mp4)

## TODO
- [x] Clean Visualization & Filtering UI
- [x] Scan selection for:
    - Object where vertices can be merged
    - Mesh objects where the origin lies outside of the bounding box boundary
    - Scan for empties that could be removed (leaf empties & empties with only one child)
- [ ] Helper to clean / reset the mesh normals