# -*- coding: utf-8 -*-
"""Extraction of the seven MOU texts published by Public Citizen on 30 August 2026
(State Department FOIA production FL-2026-00021 plus the Case Act Malawi text), and the
provenance/metadata refresh that goes with them.

  python3 extract_aug2026_release.py            # writes prog_new.json next to this file
  python3 extract_aug2026_release.py --apply    # also rewrites ../data/programmatic_tidy.csv and countries.csv

Budget rows were applied separately (see the Sep 2026 entry in the README).
Every figure is transcribed as printed in the source PDF; source errors are preserved and
flagged in the note columns rather than corrected.
"""
import sys
import json, os
# -*- coding: utf-8 -*-
"""Section 1 indicator extraction for the seven MoU texts published Aug 2026."""
PC="https://www.citizen.org/wp-content/uploads/"
SRC={'Lesotho':PC+"LESOTHO_FL-2026-00021_August-2026-Production_RELEASE.pdf",
 'Eswatini':PC+"ESWATINI_FL-2026-00021_August-2026-Production_RELEASE.pdf",
 'Sierra Leone':PC+"SIERRA-LEONE_FL-2026-00021_August-2026-Production_RELEASE.pdf",
 'Botswana':PC+"BOTSWANA_FL-2026-00021_August-2026-Production_RELEASE.pdf",
 'Madagascar':PC+"MADAGASCAR_FL-2026-00021_August-2026-Production_RELEASE.pdf",
 'Malawi':PC+"2026-0015QN-Malawi-1.13.2026.pdf",
 'Burundi':PC+"BURUNDI_FL-2026-00021_August-2026-Production_RELEASE.pdf"}
Y5=['Baseline',2026,2027,2028,2029,2030]; Y3=['Baseline',2026,2027,2028]
rows=[]
def ind(country,area,name,mtype,vals,unit,vtype,printed=None,note=None,fn=None,fnloc=None,years=None):
    for y,v in zip(years or Y5, vals):
        if v is None: continue
        rows.append({'Country':country,'Programmatic area':area,'Indicator':name,'Metric type':mtype,
          'Year':y,'Value':v,'Unit':unit,'Value type':vtype,
          'Programmatic area (as printed)':printed or area,'Unit / source note':note,
          'MoU footnote (verbatim)':fn,'MoU footnote location':fnloc,'Source (MoU PDF)':SRC[country]})
def s717(country,gov_name,detect=7,notify=1,respond=7,loc='Sec 1.3'):
    for nm,d in [('Detects suspected infectious disease outbreaks with epidemic potential within X days of disease emergence',detect),
                 ('Notifies the U.S. Government within X day(s) of detection of a confirmed infectious disease outbreak',notify),
                 ('Completes relevant initial response actions within X days of notification',respond)]:
        rows.append({'Country':country,'Programmatic area':'GHS / outbreak response','Indicator':nm,
          'Metric type':'Outbreak response (7-1-7)','Year':'Baseline','Value':d,'Unit':'days','Value type':'Days',
          'Programmatic area (as printed)':'Infectious Disease Outbreak Response Metrics','Unit / source note':
          'Standing commitment for the whole term, not a yearly target. Party named in the MOU: '+gov_name,
          'MoU footnote (verbatim)':None,'MoU footnote location':loc,'Source (MoU PDF)':SRC[country]})

# =============================================================== LESOTHO
c='Lesotho'; L='Sec 1.1 / 1.2 table, pp.1-2'
ind(c,'HIV/AIDS','% People With HIV Who Know Their Status','Outcome',[97,97,97,98,98,99],'%','Percentage')
ind(c,'HIV/AIDS','% People Who Know Their HIV Status on Treatment','Outcome',[97,97,97,98,98,99],'%','Percentage')
ind(c,'HIV/AIDS','% People On Antiretroviral Treatment (ART) Who Are Virally Suppressed','Outcome',[99]*6,'%','Percentage')
ind(c,'TB','# TB Deaths','Outcome',[1600,1200,1000,800,500,400],'count','Absolute number')
ind(c,'MCH','Maternal Mortality Rate','Outcome',[478,430,405,380,355,330],'per 100,000','Rate',
    note='The MOU prints no denominator for this row; other MOUs use per 100,000 live births.')
ind(c,'MCH','Children Under 5 Mortality Rate','Outcome',[54,51,49,46,42,40],'per 1,000','Rate')
ind(c,'HIV/AIDS','# people on ART','Process',[243507,250320,249208,247865,246359,246359],'count','Absolute number',
    note='Declines after 2026 and is flat 2029-2030.')
ind(c,'HIV/AIDS','# new HIV diagnoses among infants (0-18 months)','Process',[1604,1453,1333,1212,1107,1001],'count','Absolute number')
ind(c,'HIV/AIDS','# new HIV diagnoses among children and adults (age 18 months or older)','Process',[2498,1681,1703,1305,1336,1098],'count','Absolute number',
    note='Non-monotonic as printed: 2027 (1,703) is above 2026 (1,681) and 2029 (1,336) is above 2028 (1,305).')
ind(c,'HIV/AIDS','% pregnant and breastfeeding women living with HIV who receive ART','Process',[99]*6,'%','Percentage')
ind(c,'TB','# patients with TB notified (i.e., bacteriologically confirmed + clinically diagnosed)','Process',[6163,8769,9295,9853,9853,9853],'count','Absolute number')
ind(c,'TB','% patients with TB notified who completed treatment','Process',[81,85,88,90,90,90],'%','Percentage')
ind(c,'MCH','Median number of antenatal care visits for pregnant women','Process',[3.8,4,4,5,5,6],'visits','Count (visits)')
for suffix in ['# on ART','# Tested for HIV','# Tested for TB Screening']:
    ind(c,'Data systems & quality','% accuracy of data fields assessed during the annual data audit ('+suffix+')','Process',
        [None,85,85,90,95,98],'%','Percentage',note='No baseline printed.')
s717(c,'the Government of Lesotho',loc='Sec 1.3, p.3')

# =============================================================== ESWATINI
c='Eswatini'
efn=('2024 Baseline from: *UNAIDS Spectrum; ^Global TB report 2024; **World Bank estimates 2023; +MICS 2024. '
     'Subsequent years from National Multisectoral HIV Strategic Framework 2024-2028 and government projections.')
efl='Sec 1.1 outcome-metrics table, p.2, footnote line beneath the table'
pfn=('Data sources: 1QSCR 2025; 2HIV Annual Report 2024; 3SRH annual report 2024; 4UNAIDS Spectrum; '
     '5Global TB Report 2024; 6WHO and UNICEF estimates of national infant immunization coverage; 7World Malaria Report.')
pfl='Sec 1.2 process-metrics table, p.3, footnote line beneath the table'
b24='Baseline year 2024.'
ind(c,'HIV/AIDS','% People (15+ years) With HIV Who Know Their Status','Outcome',[98,99,99,99,99,99],'%','Percentage',note=b24+' Superscript * = UNAIDS Spectrum.',fn=efn,fnloc=efl)
ind(c,'HIV/AIDS','% People (15+ years) Who Know Their HIV Status on Treatment','Outcome',[98.5,99,99,99,99,99],'%','Percentage',note=b24+' Superscript * = UNAIDS Spectrum.',fn=efn,fnloc=efl)
ind(c,'HIV/AIDS','% People (15+ years) On Antiretroviral Treatment (ART) Who Are Virally Suppressed','Outcome',[98,99,99,99,99,99],'%','Percentage',note=b24+' Superscript * = UNAIDS Spectrum.',fn=efn,fnloc=efl)
ind(c,'Malaria','# Malaria Deaths in Children Under 5','Outcome',[0]*6,'count','Absolute number',note=b24)
ind(c,'TB','# TB Deaths (per 100,000)','Outcome',[79,49,41,35,20,10],'per 100,000','Rate',note=b24+' Superscript ^ = Global TB report 2024. Eswatini is the only MOU to express TB deaths as a rate rather than a count.',fn=efn,fnloc=efl)
ind(c,'MCH','Maternal Mortality Rate (per 100,000)','Outcome',[118,110,95,80,75,70],'per 100,000','Rate',note='Superscript ** = World Bank estimates 2023.',fn=efn,fnloc=efl)
ind(c,'MCH','Institutional Maternal Mortality Ratio (per 100,000 live births)','Outcome',[90,85,80,75,70,60],'per 100,000 live births','Rate',note='Superscript ** = World Bank estimates 2023. Unique to Eswatini among the published MOUs.',fn=efn,fnloc=efl)
ind(c,'MCH','Children Under 5 Mortality Rate (per 1000)','Outcome',[41,33,30,25,20,20],'per 1,000','Rate',note='Superscript + = MICS 2024.',fn=efn,fnloc=efl)
ind(c,'HIV/AIDS','# people on ART','Process',[214884,216496,218119,219755,220854,221958],'count','Absolute number',note='Sources 1 (QSCR 2025) and 2 (HIV Annual Report 2024).',fn=pfn,fnloc=pfl)
ind(c,'HIV/AIDS','# new HIV diagnoses among infants (0-18 months)','Process',[75,65,55,45,40,35],'count','Absolute number',note='Source 3 (SRH annual report 2024).',fn=pfn,fnloc=pfl)
ind(c,'HIV/AIDS','# new HIV diagnoses among children and adults (age 24 months or older)','Process',[3956,3800,3600,3350,3200,3000],'count','Absolute number',note='Source 4 (UNAIDS Spectrum). Age cut-off is 24 months, not the 18 months used by most other MOUs.',fn=pfn,fnloc=pfl)
ind(c,'HIV/AIDS','% pregnant and breastfeeding women living with HIV who receive ART','Process',[97,100,100,100,100,100],'%','Percentage',note='Source 3 (SRH annual report 2024).',fn=pfn,fnloc=pfl)
ind(c,'TB','# patients with TB notified (i.e., bacteriologically confirmed + clinically diagnosed)','Process',[2374,2964,3168,2851,2566,2309],'count','Absolute number',note='Source 5 (Global TB Report 2024).',fn=pfn,fnloc=pfl)
ind(c,'TB','% patients with TB notified who completed treatment','Process',[83,90,90,90,90,90],'%','Percentage',note='Source 5. 2028-2030 printed as ">90%"; stored as 90 with the inequality noted here.',fn=pfn,fnloc=pfl)
ind(c,'Polio','% surviving infants who received at least one dose of inactivated polio vaccine','Process',[70,74,79,80,85,90],'%','Percentage',note='Source 6. 2030 printed as ">=90%"; stored as 90.',fn=pfn,fnloc=pfl)
ind(c,'Immunisation (measles)','% of children aged 12-23 months who received one dose of measles-containing vaccine','Process',[85,87,89,90,90,90],'%','Percentage',note='Source 6. 2028-2030 printed as ">=90%"; stored as 90.',fn=pfn,fnloc=pfl)
ind(c,'MCH','ANC coverage','Process',[97,97,97,97,99,99],'%','Percentage',note='Source 3 (SRH annual report 2024).',fn=pfn,fnloc=pfl)
ind(c,'Data systems & quality','% accuracy of data fields assessed during the annual data audit','Process',[95]*6,'%','Percentage')
s717(c,'the GOKE (Government of the Kingdom of Eswatini)',loc='Sec 1.3, p.3')


# =============================================================== SIERRA LEONE
c='Sierra Leone'
slnote=('The Participants acknowledge that the outcome and process metrics in Sections 1.1 and 1.2 are jointly determined '
        'targets intended to guide planning, resource allocation, and performance improvement. These metrics should be '
        'reviewed periodically to reflect new data, changing epidemiology, fiscal constraints, and external shocks. '
        'Shortfalls against one or more targets should not, by themselves, constitute noncompliance with this MOU but '
        'should prompt a joint review and course correction.')
sll='Sec 1.2, p.3, paragraph beneath the process-metrics table'
b24='Baseline year 2024.'; b23='Baseline year 2023.'
ind(c,'HIV/AIDS','% People With HIV Who Know Their Status','Outcome',[87,90,95,98,98,98],'%','Percentage',note=b24,fn=slnote,fnloc=sll)
ind(c,'HIV/AIDS','% People Who Know Their HIV Status on Treatment','Outcome',[86,90,95,98,98,98],'%','Percentage',note=b24,fn=slnote,fnloc=sll)
ind(c,'HIV/AIDS','% People On Antiretroviral Treatment (ART) Who Are Virally Suppressed','Outcome',[65,90,95,98,98,98],'%','Percentage',note=b24+' A 33-point jump from baseline to 2026 - the steepest first-year outcome target in any published MOU.',fn=slnote,fnloc=sll)
ind(c,'Malaria','# Malaria Deaths in Children Under 5','Outcome',[1477,960,812,665,517,369],'count','Absolute number',note=b24)
ind(c,'TB','# TB Deaths','Outcome',[48,40,32,24,16,10],'count','Absolute number',note=b24)
ind(c,'Polio','# Polio Cases (e.g., WPV, cVDPVB)','Outcome',[15,0,0,0,0,0],'count','Absolute number',note=b24)
ind(c,'Immunisation (measles)','# Measles Cases','Outcome',[129,110,80,60,40,20],'count','Absolute number',note=b24)
ind(c,'MCH','Maternal Mortality Rate (per 100,000 live births)','Outcome',[354,279,254,229,190,140],'per 100,000 live births','Rate',note=b23+' The 2029 figure (190) breaks the constant -25 step of the preceding years; transcribed as printed.')
ind(c,'MCH','Children Under 5 Mortality Rate (per 1,000 live births)','Outcome',[94,82,78,74,70,66],'per 1,000 live births','Rate',note=b23)
ind(c,'HIV/AIDS','# people on ART','Process',[81155,85000,88000,90500,92500,94000],'count','Absolute number',note=b24)
ind(c,'HIV/AIDS','# new HIV diagnoses among infants (0-18 months)','Process',[623,529,506,489,469,447],'count','Absolute number',note=b24)
ind(c,'HIV/AIDS','# new HIV diagnoses among children and adults (age 18 months or older)','Process',[15289,12592,9592,4564,2793,1789],'count','Absolute number',note=b24)
ind(c,'HIV/AIDS','% pregnant and breastfeeding women living with HIV who receive ART','Process',[93,98,98,98,98,98],'%','Percentage',note=b24)
ind(c,'Malaria','% confirmed malaria cases that receive first-line antimalarial treatment','Process',[98,100,100,100,100,100],'%','Percentage',note=b24)
ind(c,'Malaria','# insecticide-treated nets distributed to populations at risk of malaria','Process',[364988,1137511,1062878,1197632,1228275,1531125],'routine nets','Absolute number',note=b24)
ind(c,'TB','# patients with TB notified (i.e., bacteriologically confirmed + clinically diagnosed)','Process',[22381,24744,26045,27336,28616,30618],'count','Absolute number',note=b24)
ind(c,'TB','% patients with TB notified who completed treatment','Process',[92,92,92,93,94,94],'%','Percentage',note=b24)
ind(c,'Polio','% surviving infants who received at least one dose of inactivated polio vaccine','Process',[91,93,94,95,96,97],'%','Percentage',note=b24)
ind(c,'Immunisation (measles)','% of children aged 12-23 months who received one dose of measles-containing vaccine','Process',[90,92,93,94,95,96],'%','Percentage',note=b24)
ind(c,'MCH','Median number of antenatal care visits for pregnant women (4+ visits)','Process',[86,88,89,91,93,95],'%','Percentage',note=b24+' Printed under a "median number of visits" label but the values are percentages.')
ind(c,'Data systems & quality','% accuracy of data fields assessed during the annual data audit','Process',[None,90,90,90,90,90],'%','Percentage',note='No baseline printed.')
s717(c,'the Government of Sierra Leone',loc='Sec 1.3, p.3')

# =============================================================== BOTSWANA (3-year)
c='Botswana'
bnote='Botswana is a three-year MOU: Section 1 carries targets for 2026, 2027 and 2028 only.'
ind(c,'HIV/AIDS','% People On Antiretroviral Treatment (ART) Who Are Virally Suppressed','Outcome',[98,99,100,100],'%','Percentage',note=bnote,years=Y3)
ind(c,'HIV/AIDS','Viral Load Coverage','Outcome',[58,70,90,95],'%','Percentage',note='Baseline source printed as "58% (ASLM Report)". '+bnote,years=Y3)
ind(c,'TB','# TB Deaths (% TB mortality)','Outcome',[7,5,5,3],'%','Percentage',note='Row is headed "# TB Deaths" but the values are printed as percentages (% TB mortality). '+bnote,years=Y3)
ind(c,'Polio','# Polio Cases (e.g., WPV, cVDPV)','Outcome',[0,0,0,0],'count','Absolute number',note=bnote,years=Y3)
ind(c,'Immunisation (measles)','# Measles Cases','Outcome',[1,0,0,0],'count','Absolute number',note=bnote,years=Y3)
ind(c,'MCH','Maternal Mortality Rate (per 100,000 live births)','Outcome',[176.7,155,134,112],'per 100,000 live births','Rate',note=bnote,years=Y3)
ind(c,'MCH','Children Under 5 Mortality Rate (per 1,000 live births)','Outcome',[28.7,26.6,25.2,23.8],'per 1,000 live births','Rate',note=bnote,years=Y3)
ind(c,'HIV/AIDS','# people on ART (Spectrum Goals)','Process',[341523,347036,350890,354744],'count','Absolute number',note=bnote,years=Y3)
ind(c,'HIV/AIDS','# new HIV diagnoses among infants (0-18 months) (Spectrum Goals)','Process',[22,20,16,14],'count','Absolute number',note=bnote,years=Y3)
ind(c,'HIV/AIDS','# new HIV diagnoses among children and adults (age 18 months or older)','Process',[4200,3973,3817,3674],'count','Absolute number',note=bnote,years=Y3)
ind(c,'HIV/AIDS','% pregnant and breastfeeding women living with HIV who receive ART','Process',[100,100,100,100],'%','Percentage',note=bnote,years=Y3)
ind(c,'TB','% patients with TB notified who completed treatment','Process',[68,80,82,85],'%','Percentage',note=bnote,years=Y3)
ind(c,'Polio','% surviving infants who received at least one dose of inactivated polio vaccine','Process',[80,82,84,86],'%','Percentage',note=bnote,years=Y3)
ind(c,'Immunisation (measles)','% of children aged 12-23 months who received one dose of measles-containing vaccine','Process',[77,80,82,85],'%','Percentage',note=bnote,years=Y3)
ind(c,'MCH','Median number of antenatal care visits for pregnant women','Process',[9,9,9,9],'visits','Count (visits)',note=bnote,years=Y3)
ind(c,'Data systems & quality','% accuracy of data fields assessed during the annual data audit','Process',[90,90,90,90],'%','Percentage',note='2026-2028 printed as ">90%"; stored as 90. '+bnote,years=Y3)
s717(c,'the Botswana Government',loc='Sec 1.3, p.4')

# =============================================================== MADAGASCAR
c='Madagascar'
mfn=('* The Participants plan to validate and set targets for Maternal and Child Health indicators in 2026; the '
     'Participants to the MOU intend to retroactively update to include this data once verified.')
mfl='Sec 1 outcome-metrics table, p.2, asterisk on the Maternal Mortality Rate and Children Under 5 Mortality Rate rows'
mpf=('*All figures for the indicator "percentage of surviving infants who received at least one dose of inactivated polio '
     'vaccine" are estimates based on World Bank and historical data. Targets for the indicators "children aged 12-23 months '
     'who received one dose of measles-containing vaccine" and "% of women with at least 4 ANC visits during pregnancy" are '
     'also estimated using World Bank and historical data. Targets for the indicator "accuracy of data fields assessed during '
     'the annual data audit" are estimated.')
mpl='Sec 1.2 process-metrics table, p.3, footnote paragraph beneath the table'
dec='Values printed with European decimal commas in the source (e.g. "62,3"); transcribed as decimal points.'
ind(c,'Malaria','# Malaria Deaths in Children Under 5','Outcome',[217,172,149,128,108,90],'count','Absolute number')
ind(c,'Polio','# Polio Cases (e.g., WPV, CVDPVB)','Outcome',[0]*6,'count','Absolute number')
ind(c,'Immunisation (measles)','# Measles Cases','Outcome',[2193,1096,548,274,137,68],'count','Absolute number')
ind(c,'MCH','Maternal Mortality Rate (per 100,000 live births)','Outcome',[395,370,345,320,286,295],'per 100,000 live births','Rate',
    note='SOURCE ERROR: the 2030 target (295) is WORSE than 2029 (286), reversing the trend in the final year. Transcribed as printed.',fn=mfn,fnloc=mfl)
ind(c,'MCH','Children Under 5 Mortality Rate (per 1,000 live births)','Outcome',[62.3,60.2,58.1,56,53.9,52],'per 1,000 live births','Rate',note=dec,fn=mfn,fnloc=mfl)
ind(c,'Malaria','% confirmed malaria cases that receive first-line antimalarial treatment','Process',[95.08,95.87,96.66,97.46,98.25,99.04],'%','Percentage')
ind(c,'Malaria','# insecticide-treated nets distributed to populations at risk of malaria','Process',[17420720,1715101,16705786,3919939,4529238,4982162],'routine nets','Absolute number',
    note='Erratic as printed: 2026 (1.72M) is an order of magnitude below the 17.42M baseline and the 16.71M 2027 target, and the series then drops again to 3.9-5.0M. Likely reflects mass-campaign years, but the MOU prints no note. Transcribed as printed.')
ind(c,'Polio','% surviving infants who received at least one dose of inactivated polio vaccine','Process',[63,72,75,78,81,84],'%','Percentage',fn=mpf,fnloc=mpl)
ind(c,'Immunisation (measles)','% of children aged 12-23 months who received one dose of measles-containing vaccine','Process',[60.7,67,73,78,84,90],'%','Percentage',fn=mpf,fnloc=mpl)
ind(c,'MCH','% of women with at least 4 ANC visits during pregnancy','Process',[40.4,52,57.5,63,69,75],'%','Percentage',fn=mpf,fnloc=mpl)
ind(c,'Data systems & quality','% accuracy of data fields assessed during the annual data audit','Process',[None,75,80,85,90,95],'%','Percentage',note='Baseline printed as "N/A".',fn=mpf,fnloc=mpl)
s717(c,'the Government of Madagascar',loc='Sec 1.3')

# =============================================================== MALAWI
c='Malawi'
mw='Malawi publishes the most granular Section 1 of any MOU: 19 outcome indicators, most disaggregated <15 / 15+.'
ind(c,'HIV/AIDS','Number of People Living with HIV <15','Outcome',[46832,41389,36156,31509,27525,24308],'count','Absolute number',note=mw)
ind(c,'HIV/AIDS','Number of People Living with HIV 15+','Outcome',[935012,930801,926113,921273,916311,910919],'count','Absolute number')
ind(c,'HIV/AIDS','HIV Prevalence 15+','Outcome',[7.01,6.74,6.49,6.25,6.03,5.81],'%','Percentage')
ind(c,'HIV/AIDS','% People With HIV Who Know Their Status <15','Outcome',[82,84,85,87,88,90],'%','Percentage')
ind(c,'HIV/AIDS','% People with HIV Who Know Their status 15+','Outcome',[96]*6,'%','Percentage')
ind(c,'HIV/AIDS','% People Who Know Their HIV Status on Treatment <15','Outcome',[71,73,76,78,83,85],'%','Percentage')
ind(c,'HIV/AIDS','% People who know their HIV status on Treatment 15+','Outcome',[96]*6,'%','Percentage')
ind(c,'HIV/AIDS','% People Living with HIV Who Are Virally Suppressed <15','Outcome',[49,56,62,68,75,81],'%','Percentage',
    note='Paediatric viral suppression starts at 49% against 89% for adults - the widest paediatric-adult gap in any published MOU.')
ind(c,'HIV/AIDS','% People Living with HIV Who Are Virally Suppressed 15+','Outcome',[89,89,89,89,89,90],'%','Percentage')
ind(c,'HIV/AIDS','Number of New HIV Infections <15','Outcome',[1644,1478,1362,1284,1207,1148],'count','Absolute number')
ind(c,'HIV/AIDS','Number of New HIV Infections 15+','Outcome',[8443,7303,6884,7209,7285,7766],'count','Absolute number',
    note='SOURCE ODDITY: adult new infections fall to 2027 then RISE every year to 2030 (7,766), ending above the 2027 target. Transcribed as printed.')
ind(c,'Malaria','# Malaria Deaths in Children <5 per 100,000','Outcome',[39,32,24,15,11,5],'per 100,000','Rate')
ind(c,'Malaria','# Malaria Deaths per 100,000 population','Outcome',[11,9,7,5,3,2],'per 100,000','Rate')
ind(c,'TB','TB Mortality per 100,000','Outcome',[22,16.5,16.5,14,11.5,9],'per 100,000','Rate')
ind(c,'TB','TB incidence rate per 100,000 population','Outcome',[113,108,102,97,94,91],'per 100,000','Rate')
ind(c,'Polio','# Polio Cases (e.g., WPV, cVDPVB)','Outcome',[0]*6,'count','Absolute number')
ind(c,'Immunisation (measles)','# Measles Cases','Outcome',[1068,264,66,16,4,0],'count','Absolute number')
ind(c,'MCH','Maternal Mortality Rate per 100,000','Outcome',[225,189,177,165,152,140],'per 100,000','Rate')
ind(c,'MCH','Children Under 5 Mortality Rate per 1,000','Outcome',[37.7,36.6,35.8,34.9,34.0,33.1],'per 1,000','Rate')
ind(c,'HIV/AIDS','# people on ART','Process',[897949,892021,885808,879222,873464,866843],'count','Absolute number',
    note='Declines every year, tracking the falling PLHIV estimate.')
ind(c,'HIV/AIDS','# new HIV diagnoses among infants (0-24 months)','Process',[569,505,469,444,420,402],'count','Absolute number',
    note='Age band is 0-24 months; most other MOUs use 0-18 months.')
ind(c,'HIV/AIDS','# new HIV diagnoses among children and adults (2 years and older)','Process',[44722,40107,35969,32257,28938,25943],'count','Absolute number')
ind(c,'HIV/AIDS','% pregnant and breastfeeding women living with HIV who receive ART','Process',[98]*6,'%','Percentage')
ind(c,'Malaria','% confirmed malaria cases that receive first-line antimalarial treatment','Process',[98,99,99,99,99,99],'%','Percentage')
ind(c,'Malaria','# insecticide-treated nets distributed to populations at risk of malaria','Process',[10127953,1100000,1380000,12338223,1400000,1400000],'routine nets','Absolute number',
    fn='(note: mass campaign distributions included in baseline and expected again in 2028)',
    fnloc='Sec 1.2 process-metrics table, p.3, parenthetical inside the indicator label',
    note='Malawi is the only MOU to explain its net-distribution spikes: the baseline and the 2028 peak are mass-campaign years.')
ind(c,'Malaria','% of pregnant women who have access to and receive 3 or more doses of IPTp for malaria prevention','Process',[56,60,64,68,72,80],'%','Percentage')
ind(c,'TB','# patients with TB notified (i.e., bacteriologically confirmed + clinically diagnosed)','Process',[18310,19490,18927,18359,17808,17274],'count','Absolute number')
ind(c,'TB','% patients with TB notified who completed treatment','Process',[90,92,92,93,93,94],'%','Percentage')
ind(c,'Polio','% surviving infants who received at least one dose of inactivated polio vaccine','Process',[97,97,98,99,99,99],'%','Percentage')
ind(c,'Immunisation (measles)','% of children aged 12-23 months who received one dose of measles-containing vaccine','Process',[88,89,90,92,94,95],'%','Percentage')
ind(c,'MCH','% pregnant women attending at least 4 antenatal care visits during pregnancy','Process',[78,79,80,81,82,83],'%','Percentage')
ind(c,'Data systems & quality','% accuracy of data fields assessed during the annual data audit','Process',[80,80,85,90,90,95],'%','Percentage')
s717(c,'the Government of Malawi',loc='Sec 1.3, p.4')

# =============================================================== BURUNDI
c='Burundi'
bl='Signed in English and French; where the two texts diverge the English text prevails.'
ind(c,'HIV/AIDS','% People With HIV Who Know Their Status','Outcome',[96.5,96.5,96.5,97,97,97],'%','Percentage',note=bl)
ind(c,'HIV/AIDS','% People Who Know Their HIV Status on Treatment','Outcome',[97,97,97,98,98,98],'%','Percentage')
ind(c,'HIV/AIDS','% People On Antiretroviral Treatment (ART) Who Are Virally Suppressed','Outcome',[93.3,94,94,95,95,95],'%','Percentage')
ind(c,'Malaria','# Malaria Deaths in Children Under 5','Outcome',[916,680,623,566,509,453],'count','Absolute number')
ind(c,'TB','# TB Deaths','Outcome',[170,130,100,80,60,40],'count','Absolute number')
ind(c,'Polio','# Polio Cases (e.g., WPV, cVDPVB)','Outcome',[0]*6,'count','Absolute number')
ind(c,'Immunisation (measles)','# Measles Cases','Outcome',[133,130,115,100,85,70],'count','Absolute number')
ind(c,'MCH','Maternal Mortality Rate','Outcome',[334,300,270,240,210,180],'per 100,000','Rate',note='The MOU prints no denominator for this row.')
ind(c,'MCH','Children Under 5 Mortality Rate (per 1,000 live births)','Outcome',[54,52,48,44,40,35],'per 1,000 live births','Rate')
ind(c,'HIV/AIDS','# People on ART','Process',[78285,79263,79842,80478,81141,81887],'count','Absolute number')
ind(c,'HIV/AIDS','# New HIV diagnoses among infants (0-11 months)','Process',[35,27,23,19,15,11],'count','Absolute number',
    note='Age band is 0-11 months - the narrowest of any published MOU.')
ind(c,'HIV/AIDS','# New HIV diagnoses among children and adults (age 12 months or older)','Process',[5082,4930,4854,4778,4702,4626],'count','Absolute number')
ind(c,'HIV/AIDS','% Pregnant and breastfeeding women living with HIV who receive ART','Process',[74,80,85,90,95,95],'%','Percentage')
ind(c,'Malaria','% Confirmed malaria cases that receive first-line antimalarial treatment','Process',[96.9,97,97,97.1,97.2,97.3],'%','Percentage')
ind(c,'Malaria','# Insecticide-treated nets distributed to populations at risk of malaria','Process',[1048287,1105659,1135511,1166170,1197657,1229994],'routine nets','Absolute number')
ind(c,'Data systems & quality','% Accuracy of data fields assessed during the annual data audit','Process',[84,84,84,85,88,88],'%','Percentage')
s717(c,'the Burundi Government',loc='Sec 1.3, p.3')

OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'prog_new.json')
json.dump(rows,open(OUT,'w'))
print(len(rows),'indicator rows for',len(set(r['Country'] for r in rows)),'countries ->',OUT)

if '--apply' in sys.argv:
    import pandas as pd
    d=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','data')
    os.chdir(d)
    p=pd.read_csv('programmatic_tidy.csv'); p.columns=[x.lstrip('\ufeff') for x in p.columns]
    new=pd.DataFrame(rows)[list(p.columns)]
    out=pd.concat([p,new],ignore_index=True); out.to_csv('programmatic_tidy.csv',index=False)
    print('programmatic_tidy.csv:',len(p),'->',len(out),'rows;',out.Country.nunique(),'countries')
PC="https://www.citizen.org/wp-content/uploads/"
FOIA=PC+"%s_FL-2026-00021_August-2026-Production_RELEASE.pdf"
CASE_ACT=("Published by the U.S. government on its Case Act reporting page")
FOIA_TXT=("Released by the U.S. State Department under Public Citizen's Freedom of Information Act requests "
          "(production FL-2026-00021, 6 Aug 2026)")
BOTH=("Published by the U.S. government on its Case Act reporting page, and separately released under "
      "Public Citizen's Freedom of Information Act requests (production FL-2026-00021, 6 Aug 2026)")
# country -> (symbol, route, main-text URL or None to keep, hosted-by, doc type note, specimen-sharing URL)
M={
 'Kenya':        ('*^',BOTH,None,None,None,None),
 'Rwanda':       ('^',FOIA_TXT,FOIA%'RWANDA',None,None,PC+"64193-Rwanda-Health-and-Medical-Cooperation.pdf"),
 'Liberia':      ('^',FOIA_TXT,FOIA%'LIBERIA','Public Citizen','MOU (US-Liberia); non-binding',None),
 'Lesotho':      ('^',FOIA_TXT,FOIA%'LESOTHO','Public Citizen','MOU (US-Lesotho)',PC+"64102-Lesotho-Health-Specimen-Sharing-Agreement-12.10.2025.pdf"),
 'Uganda':       ('*',CASE_ACT,None,None,None,None),
 'Eswatini':     ('^',FOIA_TXT,FOIA%'ESWATINI','Public Citizen','MOU (US-Eswatini)',PC+"64101-Eswatini-Health-Specimen-Sharing-Agreement-12.12.2025.pdf"),
 'Mozambique':   ('*^',BOTH,None,None,None,PC+"64103-Mozambique-Health-Specimen-Sharing-Agreement-12.15.2025.pdf"),
 'Cameroon':     ('^',FOIA_TXT,FOIA%'CAMEROON','Public Citizen','MOU for Durable and Resilient Health Systems (US-Cameroon); non-binding',PC+"64130-Cameroon-Health-Cooperation-Specimen-Sharing-Agreement-12.16.2025-1.pdf"),
 'Nigeria':      ('*^',BOTH,None,None,None,PC+"64104-Nigeria-Health-Specimen-Sharing-Agreement-12.19.2025.pdf"),
 'Sierra Leone': ('^',FOIA_TXT,FOIA%'SIERRA-LEONE','Public Citizen','MOU (US-Sierra Leone)',None),
 'Botswana':     ('^',FOIA_TXT,FOIA%'BOTSWANA','Public Citizen','MOU (US-Botswana); THREE-year term 2026-2028',None),
 'Ethiopia':     ('*^',BOTH,None,None,None,None),
 'Madagascar':   ('^',FOIA_TXT,FOIA%'MADAGASCAR','Public Citizen','MOU (US-Madagascar)',None),
 "Côte d'Ivoire":('^',FOIA_TXT,FOIA%'COTE-DIVOIRE','Public Citizen',"MOU on health (US-Côte d'Ivoire; doc ref No 00012); non-binding",PC+"64106-Cote-dIvoire-Health-Specimen-Sharing-Agreement-12.30.2025.pdf"),
 'Malawi':       ('*^',BOTH,PC+"2026-0015QN-Malawi-1.13.2026.pdf",'Public Citizen','MOU (US-Malawi)',PC+"64118-Malawi-Health-and-Medical-Cooperation-Specimen-Sharing-Agreement-1.13.2026.pdf"),
 'Burundi':      ('^',FOIA_TXT,FOIA%'BURUNDI','Public Citizen','MOU (US-Burundi); signed in English and French, English prevails',None),
 'Democratic Republic of the Congo':('*','Specimen sharing agreement only: published by the U.S. government on its Case Act reporting page. Main MOU text not public.',None,None,None,PC+"64189-Congo-DROC-Health-and-Medical-Cooperation.pdf"),
}
NEWTEXT={'Lesotho','Eswatini','Sierra Leone','Botswana','Madagascar','Malawi','Burundi'}
c=pd.read_csv('countries.csv')
c.columns=[x.lstrip('﻿') for x in c.columns]
for col in ['Disclosure marker','How the text became public','Specimen sharing agreement URL','Data sharing agreement URL']:
    if col not in c.columns: c[col]=None
for name,(sym,route,url,host,doc,spec) in M.items():
    m=c.Country==name
    if not m.any(): print('MISSING country row:',name); continue
    c.loc[m,'Disclosure marker']=sym
    c.loc[m,'How the text became public']=route
    if url: c.loc[m,'MoU PDF URL']=url
    if host: c.loc[m,'Hosted by']=host
    if doc: c.loc[m,'Doc type']=doc
    if spec: c.loc[m,'Specimen sharing agreement URL']=spec
    if name in NEWTEXT: c.loc[m,'Full MoU text public']='Yes'
c.loc[c.Country=='Kenya','Data sharing agreement URL']="https://healthpolicy-watch.news/wp-content/uploads/2025/12/US-Kenya-Data-Sharing-Agreement.pdf"
c.loc[c.Country=='Uganda','Specimen sharing agreement URL']="Reported to Congress; text not disclosed"
c.loc[c.Country=='Ethiopia','Specimen sharing agreement URL']="Reported to Congress; text not disclosed"
# date discrepancies found in the signed texts themselves
c['Note']=c['Note'].fillna('')
def note(country,txt):
    m=c.Country==country
    cur=c.loc[m,'Note'].iloc[0]
    c.loc[m,'Note']=(cur+' ' if cur else '')+txt
note('Malawi','Signed text reads "SIGNED on January 13, 2026"; the KFF tracker and Public Citizen both date the agreement 14 Jan 2026.')
note('Botswana','Signed text reads "SIGNED on December 22, 2025"; the KFF tracker dates it 23 Dec 2025. THREE-year MOU (2026-2028) - all other published MOUs run five years.')
note('Nigeria','Public Citizen dates the agreement 20 Dec 2025; the KFF tracker and the source PDF filename use 19 Dec 2025.')
note('Madagascar','Public Citizen records the date as "Dec. 22, 2025 or Dec. 23, 2025"; the signed text reads "SIGNED at Antananarivo on Twenty-two of December 2025".')
note('Eswatini','MOU prints a U.S. term total of $192,700,000 against the KFF tracker\'s $205,000,000; the MOU states no management-and-operations carve-out to explain the gap.')
note('Malawi','MOU prints U.S. $744,832,500 and Malawi Government $55,000,000 against the KFF tracker\'s $792,000,000 and $143,800,000.')
note('Lesotho','MOU government co-financing total is $132,495,000 (KFF tracker rounds to $132,000,000).')
c.to_csv('countries.csv',index=False)
pub=(c['Full MoU text public']=='Yes').sum()
print('countries.csv updated -',pub,'of',len(c),'texts public')
print(c[c['Full MoU text public']=='Yes'][['Country','Disclosure marker']].to_string(index=False))
