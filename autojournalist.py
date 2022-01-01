#!/usr/bin/env python3

# This doesn't do much at the moment.

import time
today = time.strftime("%Y-%m-%d")

with open('output/README.md', 'w') as markdown:
  markdown.write(f"""# NSW Covid Update for {today}

![]({today}.png)
""")

