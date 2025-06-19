import datetime
import subprocess
import urllib.parse

def get_episode_duration(url):
    url = urllib.parse.quote(url, safe='/:?&=')
    try:
        result = subprocess.run(['ffprobe', '-i', url, '-show_entries', 'format=duration', '-v', 'error', '-of', 'csv=p=0'], capture_output=True, text=True)
        if result.returncode == 0:
            duration_seconds = float(result.stdout.strip())
            hours = int(duration_seconds // 3600)
            minutes = int((duration_seconds % 3600) // 60)
            seconds = int(duration_seconds % 60)
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return "00:00:00"
    except Exception as e:
        print(f"Error getting duration for {url}: {str(e)}")
        return "00:00:00"

with open('episodes.txt', 'r') as file:
    episodes = [line.strip() for line in file.readlines()]

parsed_episodes = []

for episode in episodes:
    try:
        name, link = episode.split(': ')
        parts = name.split('_')
        if len(parts) < 3:
            date_str = parts[1].split('.')[0]
            title = parts[0]
        else:
            title, date_str, _ = parts
            date_str = date_str.replace('&amp;', '')
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        duration = get_episode_duration(link)
        print(f"Episode {title}: {duration}")
        parsed_episodes.append((date, title, link, duration))
    except Exception as e:
        print(f"Error parsing episode: {episode}\n{str(e)}")

parsed_episodes.sort(key=lambda x: x[0])

rss_items = []

for i, (date, link, duration) in enumerate(parsed_episodes):
    episode_title = f"Episode {i + 1}"
    description = f"{episode_title} was aired on {date.strftime('%Y-%m-%d')}."
    thumbnail_url = "https://d3t3ozftmdmh3i.cloudfront.net/staging/podcast_uploaded_nologo/5580833/799888d25c8aa73f}.jpeg"
    item_xml = f"""
    <item>
        <title><![CDATA[{episode_title}]]></title>
        <description><![CDATA[{description}]]></description>
        <link>{link}</link>
        <guid isPermaLink="false">{link}</guid>
        <dc:creator><![CDATA[corpse]]></dc:creator>
        <pubDate>{date.strftime("%a, %d %b %Y %H:%M:%S +0000")}</pubDate>
        <enclosure url="{link}" length="22087808" type="audio/mpeg"/>
        <itunes:summary><![CDATA[{description}]]></itunes:summary>
        <itunes:explicit>false</itunes:explicit>
        <itunes:duration>{duration}</itunes:duration>
        <itunes:image href="{thumbnail_url}"/>
    </item>
    """
    rss_items.append(item_xml)

items_xml = "\n".join(rss_items)

rss_feed = f"""
<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<rss xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:atom="http://www.w3.org/2005/Atom" version="2.0" xmlns:anchor="https://anchor.fm/xmlns" xmlns:podcast="https://podcastindex.org/namespace/1.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
    <channel>
        <title><![CDATA[Bhoot FM]]></title>
        <description><![CDATA[This is a Bengali Podcast (Bangladesh) exclusively for Bhoot FM's listeners. Bhoot FM was one of the most popular Radio Show in Bangladesh. It was aired from 2010 to 2019 at Radio Foorti 88.00 FM.]]></description>
        <link>https://github.com/shipwr3ckd/bhootfm-archives</link>
        <generator>Bython</generator>
        <lastBuildDate>{datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")}</lastBuildDate>
        <atom:link href="https://raw.githubusercontent.com/shipwr3ckd/bhootfm-archives/main/bhoot-fm.xml" rel="self" type="application/rss+xml"/>
        <author><![CDATA[corpse]]></author>
        <copyright><![CDATA[corpse]]></copyright>
        <language><![CDATA[bn]]></language>
        <image>
            <link>https://github.com/shipwr3ckd/bhootfm-archives</link>
            <title>Bhoot FM</title>
            <url>https://d3t3ozftmdmh3i.cloudfront.net/staging/podcast_uploaded_nologo/5580833/799888d25c8aa73f.jpeg</url>
        </image>
        <itunes:author>Radio Foorti</itunes:author>
        <itunes:summary><![CDATA[This is a Bengali Podcast (Bangladesh) exclusively for Bhoot FM's listeners. Bhoot FM was one of the most popular Radio Show in Bangladesh. It was aired from 2010 to 2019 at Radio Foorti 88.00 FM.]]></itunes:summary>
        <itunes:type>episodic</itunes:type>
        <itunes:owner>
            <itunes:name>corpse</itunes:name>
            <itunes:email>lmao@nuhuh.com</itunes:email>
        </itunes:owner>
        <itunes:explicit>false</itunes:explicit>
        <itunes:category text="Music"/>
        <itunes:image href="https://d3t3ozftmdmh3i.cloudfront.net/staging/podcast_uploaded_nologo/5580833/799888d25c8aa73f.jpeg"/>
        
        <!-- Episodes -->
        {items_xml}
    </channel>
</rss>
"""

try:
    with open('bhootfm-rss.xml', 'w') as file:
        file.write(rss_feed)
    print("RSS feed generated successfully: bhootfm-rss.xml")
except Exception as e:
    print(f"Error generating RSS feed: {str(e)}")
