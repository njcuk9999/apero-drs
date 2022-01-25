apero_changelog is used to prouce a nicly formatted change log from the
git commits (requires git commits to have messages).

The developer is asked whether a new version is required.
Versions must be in the form X.X.XXX where X is a number.

The recipe then updates the change log as well as update several files
throughout APERO and the documentation to update the version and date.

A git tag is also created to mark a new version.

.. warn:: This change is hard to undo. Please use carefully and check
          the current version well before making a new version

.. note:: This will add all untagged commits to this tag and version. For
          multiple commits see section 1.1.

1.1 Adding a few versions at one time
^^^^^^^^^^^^^^^^^^^^^^

If there are many commits and a few versions are required one can
add tags using `git tag {version} {commit number}` at the points
where a new version is required. Using `git log --since {date} > log.txt`
will produce a log of commit numbers since a date (set this date to the
previous verseion date). Do all but the most recent "version" this way and
then do the last one using apero_changelog and it will have the desired affect.

i.e.

.. code-block::

    git log --since 2020-09-03 > log.txt

    git tag 0.1.234 3f95c84d1f54ae70c067aa2d253de31972abe93b
    git tag 0.1.235 3f95c84d1f54ae70c067aa2d253de31972abe93b
    git tag 0.1.236 4fea06752d89151896c5258caecfd3fe12e0c64d

    apero_changelog.py    # for version 0.1.237