rmdir build /s
rmdir dist /s
rmdir PyTextNow.egg-info /s

python setup.py sdist bdist_wheel
python -m twine upload -u leogomezz4t -p Chiu2135 dist/*