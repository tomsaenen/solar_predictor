clean:
	rm -rf __pycache__/
	rm -f .DS_Store

commit:
	git commit -F .gitcommitmsg
	> .gitcommitmsg
