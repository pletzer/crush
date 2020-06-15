import vtk
from argparse import ArgumentParser
from glob import glob
import numpy
import os.path


def main(vtk_file_patterns):

    for filename in glob(vtk_file_patterns):

        print(f'file: {filename}')
        reader = vtk.vtkPolyDataReader()
        reader.SetFileName(filename)
        reader.Update()

        polydata = reader.GetOutput()

        npoints = polydata.GetNumberOfPoints()
        ncells = polydata.GetNumberOfCells()

        print(f'number of points: {npoints}')
        print(f'number of cells : {ncells}')

        # create a point array
        sum_forces = vtk.vtkDoubleArray()
        sum_forces.SetNumberOfComponents(3)
        sum_forces.SetNumberOfTuples(npoints)
        sum_forces.SetName('sum_forces')
        polydata.GetPointData().AddArray(sum_forces)

        sum_forces_data = numpy.zeros((npoints, 3), numpy.float64)

        # add the contribution from each two sets of points
        p0 = numpy.zeros(3, numpy.float64)
        p1 = numpy.zeros(3, numpy.float64)
        points = polydata.GetPoints()
        force_array = polydata.GetCellData().GetScalars('force')
        for i in range(ncells):
            cell = polydata.GetCell(i)
            ptids = cell.GetPointIds()
            npts = ptids.GetNumberOfIds()
            assert(npts == 2)
            pi0 = ptids.GetId(0)
            pi1 = ptids.GetId(1)
            points.GetPoint(pi0, p0)
            points.GetPoint(pi1, p1)

            # force
            force = p1 - p0
            force /= numpy.sqrt(force.dot(force))
            force *= force_array.GetTuple(i)[0]

            sum_forces_data[pi0, :] -= force
            sum_forces_data[pi1, :] += force

        sum_forces.SetVoidArray(sum_forces_data, npoints, 1)

        # save the new files
        writer = vtk.vtkPolyDataWriter()
        ofilename = 'sum_forces_' + os.path.basename(filename)
        writer.SetFileName(ofilename)
        writer.SetInputData(polydata)
        writer.Update()








if __name__ == '__main__':

    parser = ArgumentParser(description='Compute the total force at each node.')
    parser.add_argument('-i', dest='vtk_file_patterns', help='Specify intrs VTK file pattern (e.g. where_data/triax-intrs-\*.vtk)')
    args = parser.parse_args()
    main(args.vtk_file_patterns)