Sphinx autodocumentation
--------------------------

go to directory ``~/Documents/GitHub/excitability/docs``

generate documentations 
^^^^^^^^^^^^^^^^^^^^^^^^

sphinx-apidoc_

clean and generate rst files

.. code-block:: console

    rm source/generated/*
    sphinx-apidoc -o source/generated ../src -f --implicit-namespaces -e -H Modules -d 3

run sphinx-build to create html files

.. code-block:: console

    make clean; make html



.. _sphinx-apidoc: https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html

