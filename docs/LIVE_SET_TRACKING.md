# Live-set tracking in Google Sheets

Log one performance per row in the matching yearly tab of **Sets I've Seen**. Enter a date and artist. Use `Artist A b2b Artist B` for a joint set so each artist gets one credit. Ratings, events, notes, and attendees are optional. Unrated sets still count toward the artist's total.

`2027sets` is ready for 2027 entries. `AllShows` combines the yearly tabs. `Set history` expands joint bills and links each credit to the original performance. `Career metadata` calculates yearly counts and career totals, and `Sets Ranked` orders artists by career total. The hourly Codex sync copies `Artist counts!A:C` into the ratings workbook's `Live set counts` table as artist keys and totals. `Have Seen Live # (counts b2b)` looks up those totals.

## Add another year

1. Create a blank tab named `YYYYsets` using the latest yearly tab as the layout. Keep the headers in this order: **Date**, **Event**, **Artist(s)**, **Rating**, **Notes**, **Attendees**. Keep dates in column A and artist billing in column C. The old year's entries stay in their original tab.
2. Open the new tab and copy its numeric `gid` from the Sheets address bar. In `AllShows!A2`, copy the latest year's `HSTACK` inside `VSTACK`. Change every tab reference in the copy to the new tab and change the link's `gid` to the new tab ID. This block puts the columns in the order AllShows expects and builds the links for Set history.
3. Add the `YYYYsets` header to the yearly columns of `Career metadata`. In the `LET` formula in `A2`, copy the latest `setsInYYYY` definition and use the new year as an exact `COUNTIFS` criterion. Include that definition in the final `HSTACK` in the same position as its header. Keep **Artist** and **Total Sets Seen** in A:B. Move the **Set History** hyperlink formula to the column immediately after the expanded calculation, and make sure the native table covers the header and new column.
4. Check that existing totals agree across `Career metadata`, `Artist counts`, `Sets Ranked`, and the ratings workbook. With the first dated entry, verify the new year's count, career total, and link to the source row. The ratings workbook should pick up the new total on the next hourly sync. Keep the export and destination headers in place so the sync can recognize them.
