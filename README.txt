INSANE 98% — DIFFICULTY RANGES

1,035 charts; 68 folders; 15.2 charts per folder on average.
Counts vary from 9 to 23. D98 is our estimated scoring-ability
threshold for a 98% EX personal best; lower is easier. It is not EX%, BPI, or ★ level.
The chart ordering is unchanged from the first release; grouping is now value-based.

PICK A FOLDER
Open index.html. Select a difficulty range, use Easier/Harder, or choose All folders
to search the entire list. The page works offline. Lower bound is inclusive and
upper bound exclusive; displayed chart values are rounded.

GAME TABLE
For beatoraja-compatible players, close the game and place insane-98-ranges.bmt in
its existing table directory, then restart. This version has a different table name
from the previous release. No installation was performed in your running game.
The standard BMSTable files are index.html, header.json, and data.json. Host them
together if you need an import URL for another table importer. No public URL is hosted.

REVIEW
Read research-review.html for citations, limitations, and the new player-held-out
comparison. The two 98%-specific models were not reliably distinguished in the new
comparison, with a small numerical edge for the simpler model. The current order
was retained; it is not claimed to be uniquely best. 366 charts are provisional and 91 have no observed 98% in
the modeling cohort. Practice/popularity effects cannot be fully separated from
difficulty using personal-best snapshots.

FILES
folders.json: exact ranges and counts.
rankings.json: original estimates, ranks, chart identifiers, effort/support indicators.
validation-original.json: first release's score holdout results.
validation-player-holdout.json: additional player-held-out comparison and bootstrap.
range-build-checks.json: coverage, preserved order and folder checks.

REPRODUCTION
reproduce/make_ranges.py contains the exact regrouping rule (source paths in script).
reproduce/review_model.py contains the additional validation experiment.
The prior model generator and source manifest are also included. Scripts require
numpy/scipy and the original archive database; see prior-method-notes.txt.
Offline picker tests passed for all folders, navigation, all charts, and search.
Browser visual verification was unavailable because automated file: navigation was
blocked by the browser URL policy. No claim of in-game testing is made.
