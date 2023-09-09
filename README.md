# p2h - Pelican to Hugo reformatter
Converts markdown files from Pelican format to Hugo

Hugo (and similar Static Site Generators) expect a header that follows YAML front matter rules.

I got this idea from [Anthony Nelzin-Santos](https://anthony.nelzin.fr), who created <https://github.com/anthonynelzin/PelicanToHugo/> to do the same thing. However I wanted to be able to pass it input folders and be a little more flexible with my input parsing -- I also wanted to practice my Python for the first time in years -- so I rewrote it. 

## Usage

Run the script, including the path to your Pelican content. You can provide either a path to a single file, or a path to a whole folder:

	`python3 pelican-to-hugo.py ./Pelican/mysite/content/category/mypost.md`
	`python3 pelican-to-hugo.py ./Pelican/mysite/content/`

By default, the converted file will go to STDOUT. You can redirect this to a flie with standard redirects, or you can provide an output location:

	`python3 pelican-to-hugo.py ./Pelican/mysite/content/category/mypost.md ./Hugo/mysite/content/`
	`python3 pelican-to-hugo.py ./Pelican/mysite/content/ ./Hugo/mysite/content/`

**Note - this will not rewrite internal links or move images, etc.**

## Inferring front matter

If your input .md file relies on Pelican's inferrences, you might not explicitly include front matter such as Category or Date; if these are missing, Pelican will infer them from the file system. I've tried to do something similar.

## Licence

I've chosen GPL3 as the license for this - you're free to use it, but please submit any improvements!
