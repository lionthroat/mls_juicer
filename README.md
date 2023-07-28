# The Juicer
## Data visualization for licensed real estate agents
###### ============================================
### Problem:
###### Agents in Northern California are forced to rely on decades-old software infrastructure that hasn't substantively changed since I was a child tagging along to my mom's office. Something as simple as making a client presentation showing sold homes in their neighborhood in the last 30 days requires immense patience and tech-know to navigate the endless menus and checkboxes.
###### ============================================
### Solution:
###### I believe that real estate agents shouldn't have to be data analysts to glean important insights from market trends in their areas of focus. I also believe they should have access to personally branded data visualizations on-demand. My goal was to make a tool that is easy and quick enough to be used by agents (or their registered non-licensed assistants).
###### ============================================
### Challenges:
###### Because of controls on listing service data, the Juicer needed to be designed directly for agents, and communicated about in a way that could not be construed to be encouraging agents to inappropriately post, transmit, sell, or otherwise distribute their data. It is an ongoing and very fun challenge to try to anticipate every type of situation an agent could be facing, and then translate that into a UI that doesn't feel overwhelming, and code that can gracefully handle errors.
###### ============================================
### Implementation:
###### Code: Python 3.7
###### GUI: PyQt6
###### Data: Pandas
###### Charts: Matplotlib
###### ============================================
#### Known bugs:
1. Loading bar stopped animating
2. Switching profile does not update the last profile logged in
3. Deleting profile does not delete hdf5 file
4. Deleting profile reloads duplicate set of profile buttons
5. Title bar: minimize button not functional
6. Title bar: maximize button not functional

###### ============================================
#### Features Road Map
###### ============================================
##### Late July 2023

###### Profile Fixes
- The profile page and associated operations will be split into its own a class for better modularity
- Stacked widget for profile page: Switch profiles widget, New user widget (possible 3rd stack for confirmation deletion of a profile)
- Deletion/creation/switching profiles will have refinements
- Profile name validation: need to ensure no periods or special characters, underscores OK. Decide how to handle multi-word profiles

###### Charts
- Fix bar chart x-axis labels so that all 13 months display, and line up with labels
- Fix bar chart x-axis label format to be: Mon-YY (E.g. May-22)
- Add save-as-png button (native to matplotlib, but needs to be added back in for PyQt6)
- Implement market snapshot chart

###### Basic GUI Functionality
- Minimize/maximize buttons in title bar
- Will add small transition animations to improve the feel of interacting

###### Data Manipulation
- Need to differentiate by zip code for some Sonoma County cities and neighborhoods. It is easy to get an overcount of properties sold for Sonoma in any given month.
###### ============================================
##### August 2023

###### Modularization and testing
In August, I need to implement better overall modularization, as well as usage of unit tests, and reduction of unused imports.

###### Personal branding, color picker
- Allow user to pick their branding palette
- Save colors, fonts, etc. to profile
- Apply branding to matplotlib charts
- Create tools for user to change styles on the fly

###### ============================================
##### September 2023

###### UI and animation overhaul
In September, I will be working on an artwork and animation overhaul. That will affect the whole look and feel of the splash screen, loading animations, and the scenery banner in the program itself. There will be UI tweaks throughout.

###### Distribution
While remaining open source, I will be packaging a version for distribution by donation only, and a landing page where it can be downloaded. My aim is to make versions for Linux, Windows, and Mac.

============================================
