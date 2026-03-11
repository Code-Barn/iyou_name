shortcuts for individuals (besides home person)

filter french and english "states"


fix the place name parser. it is removing repeated names even when they should be properly designated as a county. we implemented this when there was a bad place name in the file we should have fixed the place name instead of implementing a backend fix for it. 

change show county button to only effect names with city,county,state,USA so that locations that are only county and state don't have the county stripped when checked

retain (or add?) 'county' if the US place name is only county and state. otherwise remove

for U.K. placenames use the country (ie: England, Scotland, Wales, N. Ireland) flag 

make option for "death position" to be either a) exact death location b) burial location (with fallback to death if no burial listed)

You just helped me update our [@place_name_utils.py](file:///home/user/CODE_BASE/namechart/apps/generator/utils/prototype/place_name_utils.py) and add some chart wide options to [@display_tree.html](file:///home/user/CODE_BASE/namechart/apps/hud/templates/hud/display_tree.html) but then our session crashed. Can you try to take a look at [@PLACE_NAME_UTILS.md](file:///home/user/CODE_BASE/namechart/apps/generator/utils/prototype/docs/PLACE_NAME_UTILS.md) and then survey the current state and try to update the doc to reflect the current state of things
