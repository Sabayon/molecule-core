#!/bin/sh

# Check current dir
[[ ! -d ".git" ]] && echo "this script must be executed from git repo root" && exit 1

# Check target tag
[[ -z "$1" ]] && echo "usage: $0 <new-version>" && exit 1

# Validate new version
new_tag="$1"
for cur_tag in `git tag`; do
	[[ "$cur_tag" == "$new_tag" ]] && echo "$new_tag already tagged" && exit 1
done

# Update ChangeLog
echo "Updating ChangeLog for $new_tag"
git log > docs/ChangeLog
git add docs/ChangeLog
sed -i "s/^VERSION = \".*\"/VERSION = \"$new_tag\"/" molecule/version.py
git add molecule/version.py
git commit -m "Tagging Molecule version $new_tag" docs/ChangeLog \
    molecule/version.py

# tag version
echo "Tagging version: $new_tag"
git tag $new_tag HEAD

# Push changes upstream
git push
git push --tags

echo "Now run /home/bin/tarball-new-molecule on sabayon.org"
