import numpy as np

angstrom = "\u00C5"

class Coordinates:

    def __init__(self, *args, **kwargs):
        """ 
        Create coordinates.

        Initialization is very flexible:

            >>> Coordinates(0, 1, 0)
            Coordinates(x=0.0, y=1.0, z=0.0)
            >>> Coordinates(x=3.5, y=5, z=7)
            Coordinates(x=3.5, y=5.0, z=7.0)
            >>> Coordinates([0, 0, 2.72])
            Coordinates(x=0.0, y=0.0, z=2.72)
            >>> Coordinates(array=[0, 0, 2.72])
            Coordinates(x=0.0, y=0.0, z=2.72)
        """
        self._array = kwargs.get('array', np.zeros(3))
        if len(args) == 3:
            for i, arg in enumerate(args):
                self._array[i] = arg
        elif len(args) == 1:
            if isinstance(args[0], Coordinates):
                self._array = args[0]._array
            else:
                self._array = args[0]
        # if x, y, z kwargs are present, set the array values
        if set(('x', 'y', 'z')) <= set(kwargs):
            self._array[0] = kwargs['x']
            self._array[1] = kwargs['y']
            self._array[2] = kwargs['z']
        self._units = kwargs.get('units', angstrom)
        self._array = np.array(self._array, dtype='float64')

    @property
    def x(self):
        """ Get the magnitude of the 'x' direction
        >>> Coordinates([1.5, 2.5, 3.5]).x
        1.5
        """
        return self._array[0]

    @property
    def y(self):
        """ Get the magnitude of the 'y' direction
        >>> Coordinates([1.5, 2.5, 3.5]).y
        2.5
        """
        return self._array[1]

    @property
    def z(self):
        """ Get the magnitude of the 'z' direction
        >>> Coordinates([1.5, 2.5, 3.5]).z
        3.5
        """
        return self._array[2]
   
    @property
    def array(self):
        """ Get the underlying numpy array object
        >>> Coordinates(x=1, y=2, z=3).array
        array([ 1.,  2.,  3.])
        """
        return self._array

    @property
    def units(self):
        return self._units

    def __repr__(self):
        return 'Coordinates(x={c.x}, y={c.y}, z={c.z})'.format(c=self)

    def __str__(self):
        """
        >>> str(Coordinates(x=3, y=4, z=5))
        '[ 3.  4.  5.]'
        """
        return str(self.array)
