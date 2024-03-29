Collecting data for my <a rel="me" href="https://musician.social/@top40yearsago">@top40yearsago@musician.social</a> Mastodon account.

So far, I've found the Billboard [Hot 100] in a big CSV file. The Canadian
charts are available on a government [web site][cancon], but they're all PDF
scans. The British charts are available from the
[Official Charts Company][brits].

Here are some ideas for topics:
* Top of the chart this week.
* Top of the Canadian or British charts this week.
* Chart debut. (Only for songs that made it to the top? Top 10? Top 40?)
* Enters top 40 or top 10.
* Chart exit.
* Drops out of top 10 or top 40.
* Parody of this week's top song.
* Reenters chart. (With explanation?)

Try to include a youtube or spotify link in each post. Try to spread out mentions of the same song.

To configure the Mastodon uploader app, edit your Mastodon profile, and click on
the Development section. Add a new application with read and write scopes, but
no admin or follow. Copy the access token from the new app, and paste it as the
`TOP40ACCESSTOKEN` environment variable when you run `scan_issues.py`. Also, add
a `TOP40URL` environment variable with the Mastodon server's URL. Create a
personal access token in GitHub, and configure the `GITHUBTOKEN` and
`GITHUBREPO` environment variables.

[Hot 100]: https://data.world/kcmillersean/billboard-hot-100-1958-2017
[cancon]: http://www.bac-lac.gc.ca/eng/discover/films-videos-sound-recordings/rpm/Pages/rpm.aspx
[brits]: https://www.officialcharts.com/charts/singles-chart/19790902/7501/
