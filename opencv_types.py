import dumper


def qform__cv__Mat():
    return [dumper.SimpleFormat, dumper.SeparateFormat]


def qdump__cv__Mat(d, value):
    dims = value['dims'].integer()
    if dims != 2:
        d.putEmptyValue()
        d.putPlainChildren(value)
        return

    flags = value['flags'].integer()
    channels = 1 + (flags >> 3) & 63
    rows = int(value['rows'])
    cols = int(value['cols'])

    depth = flags & 7
    if depth == 0:
        typeName = 'unsigned char'
        cvTypeName = 'CV_8U'
        elemSize = 1
    elif depth == 1:
        typeName = 'char'
        cvTypeName = 'CV_8S'
        elemSize = 1
    elif depth == 2:
        typeName = 'ushort'
        cvTypeName = 'CV_16U'
        elemSize = 2
    elif depth == 3:
        typeName = 'short'
        cvTypeName = 'CV_16S'
        elemSize = 2
    elif depth == 4:
        typeName = 'int'
        cvTypeName = 'CV_32S'
        elemSize = 4
    elif depth == 5:
        typeName = 'float'
        cvTypeName = 'CV_32F'
        elemSize = 4
    elif depth == 6:
        typeName = 'double'
        cvTypeName = 'CV_64F'
        elemSize = 8

    d.putValue('%dx%d %sC%d' % (rows, cols, cvTypeName, channels))

    address = value["data"].pointer()
    step = value['step']['p'].dereference().integer()

    d.putNumChild(1)
    if d.isExpanded():
        with dumper.Children(d):
            d.putIntItem('cols', cols)
            d.putIntItem('channels', channels)
            d.putIntItem('dims', value['dims'])
            d.putIntItem('rows', rows)
            d.putIntItem('size', value['size']['p'].dereference())
            d.putIntItem('step', step)
            with dumper.SubItem(d, 'type'):
                d.putValue(cvTypeName)
            d.putIntItem('flags', flags)
            d.putIntItem('refcount', value['u']['refcount'])
            d.putCallItem('empty()', 'bool', value, 'empty')

            with dumper.SubItem(d, "data"):
                d.putNumChild(rows)
                if d.isExpanded():
                    d.putValue("0x%x" % value["data"].integer())
                    with dumper.Children(d):
                        for i in range(rows):
                            if channels == 1:
                                d.putArrayItem(f'[{i:d}]', address + i*step, cols, typeName)
                            else:
                                with dumper.SubItem(d, f'[{i:d}]'):
                                    with dumper.Children(d):
                                        for j in range(cols):
                                            d.putArrayItem(f'[{j:d}]', address + i*step + j*channels*elemSize, channels, typeName)

    format = d.currentItemFormat()
    if format == dumper.SeparateFormat:
        if value['dims'].integer() == 2:
            d.putBoolItem('True', True)
            # img = cv2.cv.CreateImageHeader((cols,rows), depth, channels)
            # bytes = value['step'] * value['rows']
            # cv2.cv.SetData(img, d.readMemory(value['data'], bytes))
            # if channels == 1:
            #     cv2.cv.CvtColor(img, img, cv2.cv.CV_GRAY2RGB)
            # d.putField("editformat", DisplayImageData)
            # d.put('editvalue="')
            # d.put('%08x%08x%08x%08x' % (cols, rows, byteSize, 13))
            # d.put(img.data)
            # d.put('",')
            d.putDisplay('imagedata:separate', '%08x%08x%08x%08x' % (cols, rows, cols*rows, 1) + d.readMemory(value["data"], cols*rows))


def qdump__cv__Size_(d, value):
    height = value['height']
    width = value['width']
    d.putNumChild(0)
    d.putValue('(%dx%d)' % (width, height))
    template_type = d.templateArgument(value.type, 0)
    d.putType(f'cv::Size_{template_type}')
