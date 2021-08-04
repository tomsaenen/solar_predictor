clean:
	rm -rf __pycache__/

commit:
	git commit -F .gitcommitmsg
	> .gitcommitmsg
