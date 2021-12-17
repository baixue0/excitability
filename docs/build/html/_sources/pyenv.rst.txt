Python virtual environment
------------------------------------------------------

go to directory ``~/Documents/GitHub/excitability``

setup
^^^^^^

create a folder containing python interpreter for the virtual environment

.. code-block:: console

   virtualenv -p python env

activate virtual enviroment. once activated, the prompt will start with (env).

.. code-block:: console

   source env/bin/activate

verify whether the virtual environment is activated.

.. code-block:: console

   which python


Manage packages
^^^^^^^^^^^^^^^^^

install packages in the virtual environment, or python will search for the same package in other python interpreters in the computer.

.. code-block:: console

   pip install sphinx
   pip freeze


Add virtual environment to jupyter notebook
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

install jupyter using brew. uninstall existing jupyter installed with pip.

.. code-block:: console

   brew install jupyter

install the kernel for this virtual environment.

.. code-block:: console

   python -m ipykernel install --user --name env

list installed kernels and remove unwanted kernels.

.. code-block:: console

   jupyter kernelspec list
   jupyter kernelspec remove kernelname

list installed kernels and remove unwanted kernels.

.. code-block:: console

   jupyter kernelspec remove kernelname

