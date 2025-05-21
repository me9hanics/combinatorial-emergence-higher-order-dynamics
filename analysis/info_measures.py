from hoi.metrics import DTC, TC, RedundancyMMI, SynergyMMI
from hoi.metrics import Oinfo, GradientOinfo

#TODO mutual information, autocorrelation....

def compute_hoi_beh(x, nonzero_only=False, k=3, l=3):
    """This function computes the HOI using the Oinfo."""
    model = Oinfo(x, verbose=False)
    hoi = model.fit(method="binning", minsize=k, maxsize=l)
    hoi = hoi.squeeze()
    if nonzero_only:
        return hoi[hoi != 0]
    return hoi

def compute_hoi_enc(x, y, nonzero_only=False, k=3, l=3):
    """This function computes the HOI using the Oinfo."""
    model = GradientOinfo(x, y, verbose=False)
    hoi = model.fit(method="binning", minsize=k, maxsize=l)
    hoi = hoi.squeeze()
    if nonzero_only:
        return hoi[hoi != 0]
    return hoi

def compute_redundancyMMI(x, y, nonzero_only=False, k=3, l=3):
    """This function computes the HOI using the RedundancyMMI."""
    model = RedundancyMMI(x, y, verbose=False)
    hoi = model.fit(method="binning", minsize=k, maxsize=l)
    hoi = hoi.squeeze()
    if nonzero_only:
        return hoi[hoi != 0]
    return hoi

def compute_synergyMMI(x, y, nonzero_only=False, k=3, l=3):
    """This function computes the HOI using the SynergyMMI."""
    model = SynergyMMI(x, y, verbose=False)
    hoi = model.fit(method="binning", minsize=k, maxsize=l)
    hoi = hoi.squeeze()
    if nonzero_only:
        return hoi[hoi != 0]
    return hoi

def compute_TC(x, y, nonzero_only=False, k=3, l=3):
    """This function computes the HOI using the TC."""
    model = TC(x, y, verbose=False)
    hoi = model.fit(method="binning", minsize=k, maxsize=l)
    hoi = hoi.squeeze()
    if nonzero_only:
        return hoi[hoi != 0]
    return hoi

def compute_DTC(x, y, nonzero_only=False, k=3, l=3):
    """This function computes the HOI using the DTC."""
    model = DTC(x, y, verbose=False)
    hoi = model.fit(method="binning", minsize=k, maxsize=l)
    hoi = hoi.squeeze()
    if nonzero_only:
        return hoi[hoi != 0]
    return hoi

def compute_oinfo(x, y, nonzero_only=False, k=3, l=3):
    """This function computes the HOI using the Oinfo."""
    model = Oinfo(x, y, verbose=False)
    hoi = model.fit(method="binning", minsize=k, maxsize=l)
    hoi = hoi.squeeze()
    if nonzero_only:
        return hoi[hoi != 0]
    return hoi