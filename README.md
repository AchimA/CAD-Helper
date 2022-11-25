# Blender Addon: CAD Helper
Blender Addon for imported CAD assemblies.

## Functions:

In a hierarchical CAD model (with sub-assemblies and parts), select one or more of the objects. You can then:
* Recursivley select all of it's child elements
* Delete one or multiple objects in the hirarchy. All the children of the selected objects are automatically reconnected to their 'grand-parents' before they are deleted.
* Below the selected object(s); all leafes empties (empties without children) are deleted.
* **Filter selection by Size**
    * Allows you to filter all the selected parts by bounding box. Lets you specifiy a min and max size.
    * Allows you to filter all the selected parts by object type (EMPTY, MESH, CURVE, etc.)


## Yet to be implemented:

- [ ] Filter by obj type & name
- [ ] Transfer: Viewport Display -> Material Nodes
- [ ] Transfer: Material Nodes -> Viewport Display
- [ ] Import / Export: STEP via OpenCascade

# Installation:
1. Download the *.zip file onto your hard-drive
   ![Markdown image](/images/download-addon.png){width=200}
1. In Blender
    1. Got to Edit / Preferences / Add-ons
    1. Hit install and select the downloaded *.zip file
    1. Activate the addon by ticking the box

The add-on can then be accessed in the 3D view right side-bar (T-menu).