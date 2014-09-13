all: install

index.html: README.md
	pandoc $< >$@

install:
	rsync -a ./ vm2014.melt.kyutech.ac.jp

