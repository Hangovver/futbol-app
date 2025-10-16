export function toTR(k:string){ const map:Record<string,string>={
'HOME_O0.5':'Ev 0.5 ÜST','HOME_O1.5':'Ev 1.5 ÜST','HOME_O2.5':'Ev 2.5 ÜST',
'AWAY_O0.5':'Dep 0.5 ÜST','AWAY_O1.5':'Dep 1.5 ÜST','AWAY_O2.5':'Dep 2.5 ÜST',
'O1.5':'Toplam 1.5 ÜST','O2.5':'Toplam 2.5 ÜST','O3.5':'Toplam 3.5 ÜST',
'BTTS':'KG Var','BTTS_AND_O2.5':'KG & 2.5 ÜST',
'MS1':'MS 1','MS2':'MS 2','MSX':'MS X','DC_1X':'ÇŞ 1X','DC_X2':'ÇŞ X2','DC_12':'ÇŞ 12',
'DNB1':'DNB 1','DNB2':'DNB 2',
}; return map[k] || k; }