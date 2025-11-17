def Select2Widget(tfield, **kwargs):
    print(tfield)
    print(kwargs)

def test1(field, **kwargs):
    kwargs.setdefault('data-role', u'select2')
    Select2Widget(field, **kwargs)

test1((1,2,3), test='test')