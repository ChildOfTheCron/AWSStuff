## What's Up Doc?
What's Up Doc is a command line tool that aggragates multiple different AWS RSS feeds into a single summary table. The table can be sorted between the different columbs.

![HiMum](/images/whatsupDoc.jpg?raw=true "What's Up Doc")

## Purpose
The generated table attempts to summarize the most up-to-date RSS releases for the specific service and lists them by date.

I made this tool to assist me in staying up to date with the latest changes to the various AWS services. As there are so many, it is difficult to keep up with them all. This tool *should* cover all different AWS services, I compiled a list using their service catalogue but I did find a service that was unlisted. I'm happy to accept any PRs or issues logged for missing services.

## Usage
usage: aws_rss_reader.py [-h] [-f FUZZ] [-n]

options:
  -h, --help            show this help message and exit
  -f FUZZ, --fuzz FUZZ  Fuzziness level. Select 1, 2 or 3. Default is 1.
  -n, --nocache         Generate new json from template ignoring previous runs. All previous data will be lost!

Examples:

    python3 aws_rss_reader.py -n -f 1
    python3 aws_rss_reader.py  -f 1
Once a run is complete the generated html file can be found in ./output/

## Fuzziness Level
You can set 3 different fuzziness levels (-f 1/2/3)
**Level 1** - This level will check to see if the service is mentioned in any of the RSS feed titles. If it is, it'll be updated in the table.
**Level 2** - Similar to one, it'll check for both service name and also any tags. If either of these are found in the title of the RSS feed then it'll match.
**Level 3** - Similar to levels 1 and 2 but includes both the RSS feeds title and summary section of the article.

Note: The higher the level the less accurate results may be. Keep this in mind when setting.

