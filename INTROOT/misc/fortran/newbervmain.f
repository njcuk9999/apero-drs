ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
      subroutine newbervmain(alpha,delta,eqxdr,ieqxo,ma,jm,uttime,
     &     mmdld,mmphid,mmh,
     &     mua,mud,berv,bjd,bervmx)
ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
      
C      double precision alpha        !in: alpha coord in hours fraction
C      double precision delta        !in: delta coord in degrees fraction
C      double precision eqxdr         !in: equinoxe of alpha and delta
C      integer ieqxo     !in: year of measurement
C      integer ma        !in: month of measurement
C      integer jm        !in: day of mesurement
C      double precision uttime       !in: time TU in hours of measurement
C      double precision dld          !in: longitude of the observatory in degres decim
C      double precision phid         !in: declination of the observatory in degres decim
C      double precision h            !in: alt de l'observatoire en Km
C      double precision mua          !in: mvt propre en arcsec/an
C      double precision mud          !in: mvt propre en arcsec/an
C      double precision berv          !out: baricentric earth'radial velocity correct.
C      double precision bjd           !out: JD of the measure
C      double precision resultjdi         !out: integer fration of JD of the measure
C      double precision resultjdf         !out: fraction part of JD of the measure
C      double precision bervmx            !out: vr  correct max.  

C
C   ESO PROGRAM NAME : RVROHP
C
C **********************************************************************
C
C   COMPUTER : VAX
C
C   AUTHOR : D. GILLET   OHP
C
C   LATEST VERSION : 24 MAY 1993
C
C   PURPOSE :       RVR COMPUTES :
C
C    BEOV           1) BARYCENTRIC EARTH'S ORBITAL VELOCITIES
C     BCT           2) BARYCENTRIC CORRECTION TIMES
C     EDV           3) EARTH'S DIURNAL VELOCITY
C    BERV           4) BARYCENTRIC EARTH'S RADIAL  VELOCITY
C                      THIS VELOCITY IS THE TOTAL EARTH'S CORRECTION 
c                      VELOCITY
C      ST           5) SIDEREAL  TIME FROM UNIVERSAL TIME
C      UT           6) UNIVERSAL TIME FROM SIDEREAL  TIME
C                   7) GENERAL PRECESSION
C      HA           8) HOUR ANGLE
C      AM           9) AIR MASS
C     JDB          10) BARYCENTRIC JULIAN DAY
C
C   USAGE :   DATE OF THE OBSERVATION , RIGHT ASCENSION , DECLINATION
c             AND
C             EQUINOX ARE GIVEN IN THE FILE : RVR.DAT
C
C   PRECISION : DOUBLE
C
C   AUXILIARY ROUTINES : CJD,GP,VPTBDL,BTPOS,BTVIS
C
C   INFORMATION :
C                 STAR'S REST FRAME RV = STAR'S OBSERVED RV + BERV - V*
C
C                 STAR'S BARICENTRIC RV = STAR'S OBSERVED RV + BERV
C
C                 THE DIFFERENCE BETWEEN HELIOC. AND BARYC. EARTH 
c                 VELOCITIES
C                 IS NEGLIGIBLE FOR THE CLASSICAL STELLAR 
c                 SPECTROSCOPY (<15m/s)
C
C   IMPORTANT : THE LONGITUDE AND THE LATITUDE OF THE OBSERVATORY
C               ARE GIVEN IN THE MAIN PROGRAM
C
C **********************************************************************
      implicit double precision(a-h,o-z)
      double precision jd,jd0,jd0h
      dimension dvelb(3),dposb(3)
      double precision mua          
      double precision mud          
      double precision mmphid         
      double precision mmdld        
      double precision mmh         

Cf2py intent(in) alpha
Cf2py intent(in) delta
Cf2py intent(in) eqxdr
Cf2py intent(in) ieqxo
Cf2py intent(in) ma
Cf2py intent(in) jm
Cf2py intent(in) uttime
Cf2py intent(in) mmdld
Cf2py intent(in) mmphid
Cf2py intent(in) mmh
Cf2py intent(in) mua
Cf2py intent(in) mud
Cf2py intent(out) berv
Cf2py intent(out) bjd
Cf2py intent(out) bervmx

c
c.... corrige alpha et delta des mvt propres
c
      alpha=alpha+mua/cos(delta/180*3.1415)*
     &		(ieqxo*1.+(ma-1)/12.0+(jm-1)/365.25-eqxdr)*1.85E-5
      delta=delta+mud*(ieqxo*1.+(ma-1)/12.0+(jm-1)/365.25-eqxdr)*2.78E-4
c     
c.... interface with the OHP program
c     
      eqxd=eqxdr
      lahr=int(alpha)
      lamn=int((alpha-float(lahr))*60)
      case=((alpha-float(lahr))*60-float(lamn))*60
      if (delta.lt.0) then
         lc=-1
      else
         lc=1
      endif
      ldde=int(delta)
      ldmn=int((delta-float(ldde))*60)
      cdse=((delta-float(ldde))*60-float(ldmn))*60
      if (lc.lt.0) then
         ldde=abs(ldde)
         ldmn=abs(ldmn)
         cdse=abs(cdse)
      endif
      iuthr=int(uttime)
      iutmn=int((uttime-float(iuthr))*60)
      iuts=((uttime-float(iuthr))*60-float(iutmn))*60
      it=0
c
c.... calcul bervmx (calc. approx.)
      sinb=.917*sin(delta/180*3.1415)
     &     -.397*cos(delta/180*3.1415)*sin(alpha/12*3.1415)
      if (sinb.gt.1) sinb=1
      if (sinb.lt.-1) sinb=-1
      bervmx=cos(asin(sinb))*32

C *************************************************************
C DLD=WEST LONGITUDE   PHID=LATITUDE  ( IN DEGRES DECIMALS ) 
C ***************************************** La Silla 3.6m 
c      dld= +70. + (43.8/60.) 
c      phid=- 29. - (15./60.) - (25.8/3600.) 
c      h=2.444 

      dld=mmdld
      phid=mmphid
      h=mmh
c
c.... conv obs pos.
      dl=(12.*dld)/180.
      pi=3.1415926535897932384626433
      phi=(pi*phid)/180.


C ------------------------------ST AT 0HR UT GREENWICH (ST0HG)
C     REFERENCE : MEEUS J.,1980,ASTRONOMICAL FORMULAE FOR CALCULATORS
      call cjd(ieqxo,ma,jm,0,0,0,jd0h)
      t0=(jd0h-2415020.0)/36525.
      teta0=0.276919398+100.0021359*t0+0.000001075*t0*t0
      pe=dint(teta0)
      teta0=teta0-pe
      st0hg=teta0*24.
C
      if(it)22,19,22
C -------------------------------------UT -> ST (MEAN SIDEREAL TIME)
C   REFERENCE : THE ASTRONOMICAL ALMANAC 1983, P B7
C   IN 1983: 1 MEAN SOLAR DAY = 1.00273790931 MEAN SIDERAL DAYS
C   ST WITHOUT EQUATION OF EQUINOXES CORRECTION => ACCURACY +/- 1 SEC
19    ut=dfloat(iuthr)+dfloat(iutmn)/60.+dfloat(iuts)/3600.
      stg=st0hg+ut*1.00273790931
      if(stg.lt.dl)stg=stg+24.
      st=stg-dl
      if(st.ge.24.)st=st-24.
      isthr=idint(st)
      ci=dfloat(isthr)
      ci=(st-ci)*60.
      istmn=idint(ci)
      ci2=dfloat(istmn)
      ci2=(ci-ci2)*60.
      ists=idint(ci2)
      sthr=dfloat(isthr)
      stmn=dfloat(istmn)
      sts=dfloat(ists)
      go to 23
C -------------------------------------- ST -> UT
C REFERENCE : THE ASTRONOMICAL ALMANAC 1983, P B7
22    isthr=iuthr
      istmn=iutmn
      ists =iuts
      sthr=dfloat(iuthr)
      stmn=dfloat(iutmn)
      sts =dfloat(iuts )
      st=sthr+stmn/60.+sts/3600.
      gast=st+dl
      if(gast.lt.st0hg)gast=gast+24.
      ut=(gast-st0hg)/1.00273790931
      if(ut.ge.24.)ut=ut-24.
      iuthr=idint(ut)
      ci=dfloat(iuthr)
      ci=(ut-ci)*60.
      iutmn=idint(ci)
      ci2=dfloat(iutmn)
      ci2=(ci-ci2)*60.
      iuts=idint(ci2)
C --------------------------------- PRECESSION (RIGOROUS METHOD)
23    call cjd(ieqxo,ma,jm,iuthr,iutmn,iuts,jd)
      call cjd(ieqxo,1,1,0,0,0,jd0)
      eqxo=dfloat(ieqxo)+(jd-jd0)/365.25
      iahr=lahr
      iamn=lamn
      rase=case
      ic=lc
      idde=ldde
      idmn=ldmn
      rdse=cdse
      if(eqxd-eqxo)20,1,20
 20   call gp(iahr,iamn,rase,ic,idde,idmn,rdse,eqxd,eqxo)
 1    continue

C -----------------------BARYCENTRIC  EARTH'S ORBITAL VELOCITY (BEOV)
C               The subroutine VPTBDL needs ALP and DEL in EQX 2000.0
C                                                        BEOV IN KM/S
C                                  ! DPOSB(3) in UA
      call vptbdl(jd,dposb,dvelb)  ! dvelb(3) in ua/an

      ua=149597870.  ! 1 ua = 149 597 870 km
      an=31557600.   ! 1 an = 365.25*86400 = 31 557 600 sec
      do i=1,3
      dvelb(i)=dvelb(i)*ua/an    ! dvelb(3) in km/s
      enddo

C  ALP and DEL at the observational time
      dahr=dfloat(iahr)
      damn=dfloat(iamn)
      dase=rase
      alp=((dahr+damn/60.+dase/3600.)*pi)/12.
      ddde=dfloat(idde)
      ddmn=dfloat(idmn)
      ddse=rdse
      del=((ddde+ddmn/60.+ddse/3600.)*pi)/180.
      del=del*dfloat(ic)

      if(eqxo.eq.2000.0)go to 88

      iahr2=iahr
      iamn2=iamn
      rase2=rase
      ic2=ic
      idde2=idde
      idmn2=idmn
      rdse2=rdse
c Queloz modif:
      eqx2000=2000.  

      call gp(iahr2,iamn2,rase2,ic2,idde2,idmn2,rdse2,eqxo,eqx2000)
 88   continue

C  ALP2 and DEL2 at the equinox 2000.0
      dahr=dfloat(iahr2)
      damn=dfloat(iamn2)
      dase=rase2
      alp2=((dahr+damn/60.+dase/3600.)*pi)/12.
      ddde=dfloat(idde2)
      ddmn=dfloat(idmn2)
      ddse=rdse2
      del2=((ddde+ddmn/60.+ddse/3600.)*pi)/180.
      del2=del2*dfloat(ic2)

C REFERENCE: THE ASTRONOMICAL ALMANAC 1993 PAGE:B17
C            DVELB(3) = DX/DT,DY/DT,DZ/DT
C            ARE GIVEN BY VPTBDL
      beov=dvelb(1)*dcos(alp)*dcos(del)+
     1     dvelb(2)*dsin(alp)*dcos(del)+
     2     dvelb(3)*dsin(del)

C ----------------------- BARYCENTRIC  CORRECTION TIME (BCT)
C                                        BCT IN DAY
C REFERENCE: THE ASTRONOMICAL ALMANAC 1993 PAGE:B16
C              DPOSB(3) = X,Y,Z ARE GIVEN BY VPTBDL

C     0.005775517 UA/DAY = (299792.5 km/s * 86400 s)/149 597 870 km

      bct=+0.005775517*(dposb(1)*dcos(alp)*dcos(del)+
     1                  dposb(2)*dsin(alp)*dcos(del)+
     2                  dposb(3)*           dsin(del))


C ---------------------- HOUR ANGLE (HA)   AIR MASS (AM)
C  OBSERVATORY AT 0 METRE AND WITH REFRACTION CORRECTION
C  REF. YOUNG A. T. AND IRVINE W. M. ASTRON. J. 72,945,1967

      har=((sthr+stmn/60.+sts/3600.)*pi)/12.-alp
      secz=1./(dsin(del)*dsin(phi)+dcos(del)*dcos(phi)*dcos(har))
      am=secz*(1.-0.0012*(secz*secz-1.))

C -------------- EARTH'S DIURNAL VELOCITY (EDV)
C                EARTH'S RADIAL  VELOCITY (ERV)
C                EDV AND ERV IN KM/S
C Ref.=Laurence G. T., 1981, Computational Spherical Astronomy
C     Wiley, New York, page 59 for the calculation
C       of rho*cos(phi')=f[cos(phi)]
C  EDV=-gv*sin(HAR)*cos(DEL)*rho*cos(PHI')
c
      a=6378.137  !en km[merit(1983) see p k13 astron. almanac 1992]
      f=1./298.257  ! [merit(1983)    "    "        "      " ]
      w=7.292115 d-5  ! en rad/sec [iugg(1980)   "   "      " ]
      gv=a*w   ! gv=0.465101108 km/s = geoc velocity of the observer

      u=dcos(phi)*dcos(phi)+(1.-f)*(1.-f)*dsin(phi)*dsin(phi)
      gc=a/dsqrt(u)

      edv=-gv*dsin(har)*dcos(del)*((gc+h)/a)*dcos(phi)

      erv=beov+edv


c
c.... transfert des resultats
c
      berv=erv
      bjd=jd+bct
      resultjdi=int(jd+bct)
      resultjdf=jd+bct-nint(resultjdi)

      end



C   ROUTINE NAME : CJD
C *****************************************************************************
C   
C   PURPOSE : CALCULATION OF THE JULIAN DAY
C
C   REFERENCE : MEEUS J.,1980, ASTRONOMICAL FORMULAE FOR CALCULATORS
C
C *****************************************************************************
      subroutine cjd(iy,m,id,iuthr,iutmn,iuts,jd)
      implicit double precision(a-h,o-z)
      double precision jd
      ut=dfloat(iuthr)/24.+dfloat(iutmn)/1440.+dfloat(iuts)/86400.
      if(m-2)1,1,2
 2    iyp=iy
      mp=m
      go to 3
 1    iyp=iy-1
      mp=m+12
 3    continue
      c=iy*1.+m*1.d-2+id*1.d-4+ut*1.d-6
      if(c-1582.1015)5,4,4
 4    yp=dfloat(iyp)
      ia=idint(yp/100.d0)
      a=dfloat(ia)
      ib=2-ia+idint(a/4.d0)
      go to 6
 5    ib=0
 6    p=dfloat(mp)
      jd=dint(365.25d0* yp)+dint(30.6001d0*(p+1.d0))+dfloat(id)+ut
     *+dfloat(ib)+1720994.5d0
      e1=dint(365.25d0*yp)
      e2=dint(30.6001*(p+1.d0))
      e3=dfloat(id)
      e4=ut
      e5=dfloat(ib)
      return
      end


C
C   ROUTINE NAME : GP
C
C *****************************************************************************
C
C   PURPOSE : CALCULATION OF THE GENERAL PRECESSION FOR TWO GIVEN EPOCHS
C
C   REFERENCES : MEEUS J.,1980,ASTRONOMICAL FORMULAE FOR CALCULATORS
C                EXPLANATORY SUPPLEMENT TO ASTRONOMICAL EPHEMERIS 1961,P30-31
C                MODIFIED BARBIER'S ROUTINE ESO LA SILLA,1981
C
C *****************************************************************************
      subroutine gp(iahr,iamn,rase,ic,idde,idmn,rdse,e0,e1)
      implicit double precision(a-h,o-z)
C ---------------------------------
      pi=3.1415926535897932384626433
      conv=pi/(180.*3600.)
      radhr=12./pi
      strad=(1./3600.)/radhr
      sarad=strad/15.
C ---------------------------------
      a0=((iahr*60.+iamn)*60.+rase)*strad
      d0=dfloat(ic)*((dfloat(idde)*60.+dfloat(idmn))*60.+rdse)*sarad
C ---------------------------------
      t0=(e0-1900.)/100.
      t=(e1-e0)/100.
      dz0=(2304.25+1.396*t0+(0.302+0.0179*t)*t)*t*conv
      z0=dz0+(0.791+0.0013*t)*t*t*conv
      adz0=a0+dz0
      th0=(2004.682-0.853*t0-(0.426+0.0416*t)*t)*t*conv
C ---------------------------------
      q=dsin(th0)*(dtan(d0)+dcos(adz0)*dtan(th0/2.))
      te=datan(q*dsin(adz0)/(1.-q*dcos(adz0)))
      alp=adz0+te+z0
      alp=alp*radhr
      if(alp.gt.24.)alp=alp-24.
      if(alp.lt.0.)alp=alp+24.
C
      a=dcos(d0)*dsin(adz0)
      b=dcos(th0)*dcos(d0)*dcos(adz0)-dsin(th0)*dsin(d0)
      cdel=dsqrt(a*a+b*b)
      del=dacos(cdel)
C ---------------------------------
      iahr=alp
      rmn=(alp-iahr)*3600.
      iamn=rmn/60.
      rase=rmn-iamn*60.
C ---------------------------------
      del=del/sarad
      if(del.lt.0.)ic=-1
      if(del.lt.0.)del=-1.*del
      idde=dint(del/3600.)
      smn=del-dfloat(idde)*3600.
      idmn=dint(smn/60.)
      rdse=smn-dfloat(idmn)*60.
      return
      end


cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
      subroutine vptbdl(dj,xyzdat,xyzpdat)
cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
c                                        *****************************  
c Position et vitesse de la Terre        From Pierre Bretagnon 23/5/93
c                                        *****************************
c release 11 mai 1994  
c                                                                       
c IL CALCULE LA POSITION ET LA VITESSE DE LA TERRE PAR RAPPORT AU       
c BARYCENTRE DU SYSTEME SOLAIRE 
c		dans l'equateur moyen et l'equinoxe de la date 
C	(REM:DQ3/6/95, c'est la modif 94)                             
c                                                                       
c SUBROUTINE BTPOS  : POSITION DE LA TERRE A LA PRECISION DE 8.D-5 UA   
c                                           (= 11968 km ou 0.040 sec)
c SUBROUTINE BTVIT  : VITESSE DE LA TERRE A LA PRECISION DE 1.8D-5 UA/AN
c                                                          (= 0.09 M/S) 
c                                                                       
      implicit double precision (a-h,o-z)
      dimension xyz(3),xyzp(3), xyzdat(3), xyzpdat(3)
                                                                       
      call btpos(dj,xyz,xyzdat)
      call btvit(dj,xyzp,xyzpdat)
      return
      end

cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
      subroutine btpos(dj,xyz,xyzdat)
cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
c                                                                       
c  SOLUTION EXTRAITE DE LA THEORIE PLANETAIRE VSOP87E           
c  (P. BRETAGNON, G. FRANCOU, 1988, AA 202, 309).             
c  CE SOUS-PROGRAMME CALCULE, POUR LA DATE JULIENNE DJ, LES COORDONNEES XYZ
c  DU VECTEUR BSS-T RAPPORTEES A L'EQUATEUR MOYEN ET L'EQUINOXE J2000.
c + (rel) que les coordonnees xyzdat rapportees a l'equateur moyen et
c   l'equinoxe de la date. 
c                 BSS = BARYCENTRE DU SYSTEME SOLAIRE                   
c                   T = CENTRE DE LA TERRE                              
c   LE RESULTAT EST EN UNITES ASTRONOMIQUES (1 UA = 149 597 870 000 M)  
c   PRECISION : 8.D-5 UA SUR L'INTERVALLE 1900-2100.                    
c                                                                       
      implicit double precision (a-h,o-z)
      dimension xa0(24,3),xb0(24,3),xc0(24,3),xa1(2,3),xb1(2,3),xc1(2,3)
      dimension xyz(3),nxyz(2,3),dmat(3,3),xyzdat(3)
c                                                                       
      data dj0/2451545.d0/
      data nxyz/24,2,24,2,5,1/
c                                                                       
c LE CALCUL EST D'ABORD EFFECTUE DANS L'ECLIPTIQUE PUIS DANS L'EQUATEUR 
c MOYEN J2000 PAR UNE ROTATION DE  EPSILON(J2000) = 23D 26' 21.412". ON 
c A BESOIN DE SINUS ET DE COSINUS DE EPSILON : SINE ET COSE.            
c                                                                       
      data sine/0.397776996d0/
      data cose/0.917482131d0/
c                                                                     
      data  xa0/
     .        0.99982624851d+00, 0.83525476082d-02, 0.59051845530d-02,
     .        0.49312058479d-02, 0.27165068635d-02, 0.15543421987d-02,
     .        0.83789103921d-03, 0.11821467403d-03, 0.10466596187d-03,
     .        0.76144862476d-04, 0.31108383566d-04, 0.19402843976d-04,
     .        0.19412286640d-04, 0.18878157278d-04, 0.21372562585d-04,
     .        0.17091028079d-04, 0.17078815351d-04, 0.14272814046d-04,
     .        0.13991189991d-04, 0.11861089741d-04, 0.14452415265d-04,
     .        0.10910055154d-04, 0.93442917275d-05, 0.81368494152d-05,
c                                                                       
     .        0.99988907017d+00, 0.24088295012d-01, 0.83528977397d-02,
     .        0.49296603666d-02, 0.27203303304d-02, 0.15544284911d-02,
     .        0.83751909527d-03, 0.11819755209d-03, 0.10466933158d-03,
     .        0.76230323236d-04, 0.31108378230d-04, 0.19629132136d-04,
     .        0.19407038856d-04, 0.18904805835d-04, 0.21474732013d-04,
     .        0.17092189532d-04, 0.17079869619d-04, 0.14299328771d-04,
     .        0.13986608673d-04, 0.11857892113d-04, 0.14402647698d-04,
     .        0.11350919213d-04, 0.93453922442d-05, 0.81307715717d-05,
c                                                                       
     .        0.11810174339d-03, 0.11270510922d-03, 0.48020482632d-04,
     .        0.11310462973d-04, 0.11537418361d-04, 19*0.d0/
      data  xb0/
     .        0.17534856847d+01, 0.17103453946d+01, 0.62831851967d+01,
     .        0.37411583445d+01, 0.40160144028d+01, 0.21705206576d+01,
     .        0.23396772639d+01, 0.40459915129d+01, 0.16672264522d+01,
     .        0.32405253591d+01, 0.66875219801d+00, 0.10123664776d+01,
     .        0.47989191383d+01, 0.23906379473d+01, 0.10923518967d+01,
     .        0.49540223397d+00, 0.13002983234d+00, 0.38690127711d+01,
     .        0.58069911412d+01, 0.77647243459d+00, 0.28104574696d+01,
     .        0.36898478246d+01, 0.60738992258d+01, 0.32548361188d+01,
c                                                                       
     .        0.18265890456d+00, 0.31415926598d+01, 0.13952879005d+00,
     .        0.21705245840d+01, 0.24444363555d+01, 0.59927021065d+00,
     .        0.76880010707d+00, 0.24752444885d+01, 0.96416905576d-01,
     .        0.16689661754d+01, 0.53811412607d+01, 0.57075673434d+01,
     .        0.32280826763d+01, 0.39621984697d+01, 0.26625353890d+01,
     .        0.52078040107d+01, 0.17008567195d+01, 0.23018451326d+01,
     .        0.10944404756d+01, 0.54884596691d+01, 0.43825036605d+01,
     .        0.52731341522d+01, 0.45030120184d+01, 0.16839344262d+01,
c                                                                       
     .        0.46078312048d+00, 0.41685732455d+00, 0.45826472337d+01,
     .        0.57587713904d+01, 0.31415926536d+01, 19*0.d0/
      data  xc0/
     .        0.62830758500d+01, 0.12566151700d+02, 0.00000000000d+00,
     .        0.52969096509d+00, 0.21329909544d+00, 0.38133035638d-01,
     .        0.74781598567d-01, 0.10593819302d+01, 0.18849227550d+02,
     .        0.42659819088d+00, 0.83996847318d+02, 0.20618554844d+00,
     .        0.14956319713d+00,-0.22041264244d+00, 0.15773435424d+01,
     .        0.62795527316d+01,-0.62865989683d+01, 0.52257741809d+00,
     .       -0.53680451210d+00, 0.76266071276d-01,-0.23528661538d+01,
     .        0.52236939198d+01, 0.12036460735d+02, 0.36648562930d-01,
c                                                                       
     .        0.62830758500d+01, 0.00000000000d+00, 0.12566151700d+02,
     .        0.52969096509d+00, 0.21329909544d+00, 0.38133035638d-01,
     .        0.74781598567d-01, 0.10593819302d+01, 0.18849227550d+02,
     .        0.42659819088d+00, 0.83996847318d+02, 0.20618554844d+00,
     .        0.14956319713d+00,-0.22041264244d+00, 0.15773435424d+01,
     .        0.62795527316d+01,-0.62865989683d+01, 0.52257741809d+00,
     .       -0.53680451210d+00, 0.76266071276d-01,-0.23528661538d+01,
     .        0.52236939198d+01, 0.12036460735d+02, 0.36648562930d-01,
c                                                                       
     .        0.21329909544d+00, 0.52969096509d+00, 0.38133035638d-01,
     .        0.74781598567d-01, 0.00000000000d+00, 19*0.d0/
      data  xa1/
     .        0.12210698202d-05, 0.51499999680d-06,
c     DATA  YA1/                                                        
     .        0.93052440783d-06, 0.51506452946d-06,
c     DATA  ZA1/                                                        
     .        0.22782175000d-05, 0.d0/
      data  xb1/
     .        0.20357085573d-07, 0.60026626720d+01,
c     DATA  YB1/                                                        
     .        0.62831852717d+01, 0.44318049929d+01,
c     DATA  ZB1/                                                        
     .        0.34137250428d+01, 0.d0/
      data  xc1/
     .        0.00000000000d+00, 0.12566151700d+02,
c     DATA  YC1/                                                        
     .        0.00000000000d+00, 0.12566151700d+02,
c     DATA  ZC1/                                                        
     .        0.62830758500d+01, 0.d0/
c**                                                                     
      t=(dj-dj0)/365.25d0
C      if(abs(t).ge.101) then
C        write(6,1300) t+2000
C1300    format(1x,'DATE',f9.2,' EN DEHORS DE L''INTERVALLE 1900-2100')
C        stop 1111
C      endif
c**                                                                     
      do 1 j=1,3
        xyz(j)=0.d0
        do 2 k=1,nxyz(1,j)
          xyz(j)=xyz(j)+xa0(k,j)*cos(xb0(k,j)+xc0(k,j)*t)
2       continue
        do 3 k=1,nxyz(2,j)
          xyz(j)=xyz(j)+xa1(k,j)*t*cos(xb1(k,j)+xc1(k,j)*t)
3       continue
1     continue
c                                                                       
c     CALCUL DES COORDONNEES EQUATORIALES MOYENNES J2000                      
c                                                                       
      yy=xyz(2)
      zz=xyz(3)
      xyz(2)=yy*cose-zz*sine
      xyz(3)=yy*sine+zz*cose

c                                                                      
c  calcul des coordonnees equatoriales de la date                       
c                                                                      
c  dmat est la matrice de precession qui fait passer des coordonnees    
c  equatoriales j2000 aux coordonnees equatoriales de la date; elle est 
c  calculee ici a la precision de 3.d-7 sur l'intervalle (1900,2100).   
c                                                                       
      dmat(1,1)=1.d0-297.202d-10*t**2                                   
      dmat(1,2)=-22.36049d-5*t-6.775d-10*t**2                           
      dmat(1,3)= -9.71665d-5*t+2.068d-10*t**2                           
      dmat(2,1)= -dmat(1,2)                                             
      dmat(2,2)=1.d0-249.996d-10*t**2                                   
      dmat(2,3)=    -108.634d-10*t**2                                   
      dmat(3,1)= -dmat(1,3)                                             
      dmat(3,2)=  dmat(2,3)                                             
      dmat(3,3)=1.d0 -47.206d-10*t**2                                   
c                                                                       
      do 10 i=1,3                                                       
        xyzdat(i)=0.d0                                                  
        do 11 j=1,3                                                     
          xyzdat(i)=xyzdat(i)+dmat(i,j)*xyz(j)                          
11      continue                                                       
10    continue   
      return
      end

cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
      subroutine btvit(dj,xyzp,xyzpdat)
cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
      implicit double precision (a-h,o-z)
c                                                                       
c     SOLUTION EXTRAITE DE LA THEORIE PLANETAIRE VSOP87E           
c     (P. BRETAGNON, G. FRANCOU, 1988, AA 202, 309).             
c   CE SOUS-PROGRAMME CALCULE, POUR LA DATE JULIENNE DJ, LES COORDONNEES    
c   XYZP DU VECTEUR VITESSE DE BSS-T RAPPORTEES A L'EQUATEUR MOYEN ET   
c   L'EQUINOXE J2000 ainsi que les coordonnees xyzpdat rapportees a     
c   l'equateur moyen et l'equinoxe de la date. 
c                 BSS = BARYCENTRE DU SYSTEME SOLAIRE                   
c                   T = CENTRE DE LA TERRE                              
c   LE RESULTAT EST EN UNITES ASTRONOMIQUES PAR AN                      
c     (1 UA = 149 597 870 000 M ; 1 AN = 365.25*86400 = 31 557 600 S)   
c   PRECISION : 1.8D-5 UA/AN = 0.09 M/S SUR L'INTERVALLE 1900-2100.     
c   DJ doit etre calcule ###


c                                                                       
      dimension xpa0(129,3),xpb0(129,3),xpc0(129,3),
     .    xpa1(5,3),xpb1(5,3),xpc1(5,3),xpa2(1,3),xpb2(1,3),xpc2(1,3)
      dimension xyzp(3),nxyz(3,3),dmat(3,3),xyzpdat(3)
c                                                                       
      data dj0/2451545.d0/
      data nxyz/129,5,1,128,5,1,17,2,1/
c                                                                       
c LE CALCUL EST D'ABORD EFFECTUE DANS L'ECLIPTIQUE PUIS DANS L'EQUATEUR 
c MOYEN J2000 PAR UNE ROTATION DE  EPSILON(J2000) = 23D 26' 21.412". ON 
c A BESOIN DE SINUS ET DE COSINUS DE EPSILON : SINE ET COSE.            
c   enfin, on passe des coordonnees j2000 (xyzp) aux coordonnees de la
c date (xyzpdat) par la matrice de precession dmat
c                                                                       
      data sine/0.397776996d0/
      data cose/0.917482131d0/
c**                                                                     
      data xpa0/
     .        0.62819841590d+01, 0.10495891010d+00, 0.19728607475d-02,
     .        0.26130061447d-02, 0.26120150581d-02, 0.57942858622d-03,
     .        0.12523034421d-03, 0.14364704464d-03, 0.10736565424d-03,
     .        0.10732602253d-03, 0.11247220252d-03, 0.77365417761d-04,
     .        0.73778767356d-04, 0.62658825872d-04, 0.59271787104d-04,
     .        0.56990758974d-04, 0.39077300964d-04, 0.41641944483d-04,
     .        0.39377368703d-04, 0.40912678176d-04, 0.28361375603d-04,
     .        0.28278039100d-04, 0.26995655075d-04, 0.26590592984d-04,
     .        0.35574465261d-04, 0.32475554281d-04, 0.24735070074d-04,
     .        0.34004601621d-04, 0.33711873230d-04, 0.32066009210d-04,
     .        0.31128221141d-04, 0.29485604173d-04, 0.24645471121d-04,
     .        0.16086081913d-04, 0.18652021405d-04, 0.14748515983d-04,
     .        0.11204409037d-04, 0.11204168974d-04, 0.10371508070d-04,
     .        0.91274730181d-05, 0.88452068336d-05, 0.10602790799d-04,
     .        0.76926993414d-05, 0.68330535556d-05, 0.68678394153d-05,
     .        0.88195464439d-05, 0.74876126219d-05, 0.75049880742d-05,
     .        0.74643075883d-05, 0.69926171482d-05, 0.63960322663d-05,
     .        0.66688494079d-05, 0.47892280690d-05, 0.63395651636d-05,
     .        0.60049701178d-05, 0.42559619196d-05, 0.39690016399d-05,
     .        0.39602559034d-05, 0.43907212217d-05, 0.52462449082d-05,
     .        0.49112398439d-05, 0.48074174933d-05, 0.35841563605d-05,
     .        0.34685967936d-05, 0.41535151650d-05, 0.38761211268d-05,
     .        0.40082939135d-05, 0.36178813424d-05, 0.36169609912d-05,
     .        0.45176158102d-05, 0.42592573149d-05, 0.32159606555d-05,
     .        0.41947739183d-05, 0.31713168504d-05, 0.30962101948d-05,
     .        0.30398337417d-05, 0.35384438847d-05, 0.30520890668d-05,
     .        0.27180193882d-05, 0.24882133287d-05, 0.24840237303d-05,
     .        0.33246565813d-05, 0.29030647889d-05, 0.24825475633d-05,
     .        0.29242347542d-05, 0.27858429899d-05, 0.21680827968d-05,
     .        0.17816206686d-05, 0.22657511173d-05, 0.23179070012d-05,
     .        0.20120794581d-05, 0.18364947616d-05, 0.20797037254d-05,
     .        0.18774376413d-05, 0.17449726625d-05, 0.14509855925d-05,
     .        0.16562008817d-05, 0.16080967117d-05, 0.19457762173d-05,
     .        0.14182230823d-05, 0.15390779522d-05, 0.18089443616d-05,
     .        0.17495319775d-05, 0.18187203010d-05, 0.14821751026d-05,
     .        0.12765576823d-05, 0.13542988434d-05, 0.17148647946d-05,
     .        0.15750590930d-05, 0.12002384427d-05, 0.12552488486d-05,
     .        0.13739992330d-05, 0.13241128442d-05, 0.12092213718d-05,
     .        0.11998914041d-05, 0.13750572644d-05, 0.11643873668d-05,
     .        0.13880098097d-05, 0.11483578630d-05, 0.10573900064d-05,
     .        0.13345471533d-05, 0.10424788691d-05, 0.12406995146d-05,
     .        0.10229582702d-05, 0.12027160416d-05, 0.12210698202d-05,
     .        0.11353564315d-05, 0.10520473191d-05, 0.10003891373d-05,
c     DATA YPA0/                                                        
     .        0.62823788667d+01, 0.10496330986d+00, 0.19729242635d-02,
     .        0.26130056965d-02, 0.26111966837d-02, 0.58024386193d-03,
     .        0.12521220815d-03, 0.14364700775d-03, 0.10737228179d-03,
     .        0.10733331592d-03, 0.11248544850d-03, 0.77274400428d-04,
     .        0.73895547975d-04, 0.62631022764d-04, 0.59293754361d-04,
     .        0.59275076399d-04, 0.39069016373d-04, 0.41649387030d-04,
     .        0.36782578817d-04, 0.39859359241d-04, 0.28389830897d-04,
     .        0.28282098209d-04, 0.27001593637d-04, 0.26508127550d-04,
     .        0.35580532589d-04, 0.25257982439d-04, 0.32512000229d-04,
     .        0.33887499861d-04, 0.30368016104d-04, 0.33873035419d-04,
     .        0.32060686804d-04, 0.31131262582d-04, 0.29485599259d-04,
     .        0.24319149943d-04, 0.16089266948d-04, 0.18569865962d-04,
     .        0.14748480135d-04, 0.11201354928d-04, 0.11201594930d-04,
     .        0.91325887421d-05, 0.10692675462d-04, 0.11205001669d-04,
     .        0.82177406779d-05, 0.77320850188d-05, 0.68327563652d-05,
     .        0.69224405351d-05, 0.88195462657d-05, 0.74781718152d-05,
     .        0.75025312609d-05, 0.72725447953d-05, 0.63764465529d-05,
     .        0.65730077452d-05, 0.47934140905d-05, 0.63361716684d-05,
     .        0.60028220687d-05, 0.39690010892d-05, 0.39602564507d-05,
     .        0.43907177235d-05, 0.52465884944d-05, 0.49008065485d-05,
     .        0.49128569508d-05, 0.41853466577d-05, 0.35841563340d-05,
     .        0.41593763739d-05, 0.40549844108d-05, 0.36178813424d-05,
     .        0.36169609912d-05, 0.45124681519d-05, 0.42585288321d-05,
     .        0.32167397300d-05, 0.41972270961d-05, 0.31807687223d-05,
     .        0.31643474467d-05, 0.30865011136d-05, 0.34275803602d-05,
     .        0.30398367881d-05, 0.35384439112d-05, 0.34356671841d-05,
     .        0.30452873980d-05, 0.27180192402d-05, 0.24836669791d-05,
     .        0.29022801393d-05, 0.23310283295d-05, 0.31110854563d-05,
     .        0.24873419195d-05, 0.29659308400d-05, 0.21681087749d-05,
     .        0.22683803337d-05, 0.17817074599d-05, 0.23266799211d-05,
     .        0.18295265984d-05, 0.23180335498d-05, 0.20147373799d-05,
     .        0.18805912550d-05, 0.19739452718d-05, 0.20252150128d-05,
     .        0.17455131244d-05, 0.16237909856d-05, 0.19285985086d-05,
     .        0.19457773104d-05, 0.14271607526d-05, 0.15379644975d-05,
     .        0.18183636162d-05, 0.14815995572d-05, 0.13577243619d-05,
     .        0.16082245882d-05, 0.13333473883d-05, 0.15754562131d-05,
     .        0.16412375855d-05, 0.11943740764d-05, 0.13744384070d-05,
     .        0.12201039835d-05, 0.12642328783d-05, 0.12075317312d-05,
     .        0.11988044592d-05, 0.13753787760d-05, 0.11649598142d-05,
     .        0.13867556350d-05, 0.11479568531d-05, 0.13269887984d-05,
     .        0.10425333318d-05, 0.12395290951d-05, 0.12555448071d-05,
     .        0.10227600378d-05, 0.10509970279d-05, 0.11558939675d-05,
     .        0.10522915407d-05, 0.10037515349d-05, 0.d0,
c     DATA ZPA0/                                                        
     .        0.23581686411d-03, 0.59695452636d-04, 0.25196301200d-04,
     .        0.12903261274d-04, 0.73671091064d-05, 0.55969940206d-05,
     .        0.42029803966d-05, 0.28848341554d-05, 0.25337808460d-05,
     .        0.26485391051d-05, 0.18312184701d-05, 0.15846234571d-05,
     .        0.14084829407d-05, 0.13663147382d-05, 0.13244112428d-05,
     .        0.10319271203d-05, 0.11378705858d-05, 112*0.d0/
      data xpb0/
     .        0.33242820099d+01, 0.32811437224d+01, 0.32380254479d+01,
     .        0.22395485248d+01, 0.53119547853d+01, 0.55868097655d+01,
     .        0.56167571069d+01, 0.45951044041d+01, 0.48424252741d+01,
     .        0.20661920943d+01, 0.13615101967d+01, 0.30322627825d+01,
     .        0.47465064529d+01, 0.39104733769d+01, 0.37413170279d+01,
     .        0.52606444165d+01, 0.31948924254d+01, 0.67239816607d+00,
     .        0.28777805159d+01, 0.60037576464d+01, 0.65686655197d+00,
     .        0.34330343447d+01, 0.21159978790d+01, 0.13752948670d+01,
     .        0.56428958073d+01, 0.48114642109d+01, 0.60729357932d+01,
     .        0.12396609741d+01, 0.26631481737d+01, 0.24941681741d+01,
     .        0.38363590152d+01, 0.39977415127d+01, 0.11396887065d+01,
     .        0.34729653354d+01, 0.44079175459d+01, 0.70111561004d-01,
     .        0.15313580656d+01, 0.43077242717d+01, 0.61726703451d+01,
     .        0.57786427654d+01, 0.30441700987d+01, 0.48432322710d+01,
     .        0.52223593677d+01, 0.58420865541d+01, 0.34152438230d+01,
     .        0.66747500623d+00, 0.52158118418d+01, 0.42360974057d+01,
     .        0.54399083616d+01, 0.59332829614d+00, 0.56049562454d+01,
     .        0.44817673745d+01, 0.61937466923d+01, 0.10721112089d+01,
     .        0.36228615009d+01, 0.51547211574d+01, 0.59780902513d+01,
     .        0.24711475656d+01, 0.53380203562d+01, 0.21253466355d+01,
     .        0.57303666412d+01, 0.40644740385d+01, 0.48862453145d+01,
     .        0.48980567897d+01, 0.81960573136d+00, 0.23020227310d+01,
     .        0.25834003083d+01, 0.74267260198d+00, 0.42496144717d+01,
     .        0.20249770785d+01, 0.14779155616d+01, 0.28833537850d+01,
     .        0.39255826013d+01, 0.63588959818d+00, 0.55796513199d+01,
     .        0.20686954509d+01, 0.20520683654d+01, 0.29886868061d+01,
     .        0.62060398951d+01, 0.41396022589d+00, 0.13128733998d+01,
     .        0.20650766463d+01, 0.86570913941d-01, 0.46916390413d+01,
     .        0.35738134141d+00, 0.47320334812d+01, 0.60653382301d+01,
     .        0.48482119519d+00, 0.58742808036d+01, 0.59785173917d+01,
     .        0.40624938927d+01, 0.51981002285d-01, 0.34903147177d+01,
     .        0.26347620926d+01, 0.31958443684d+00, 0.30379397958d+01,
     .        0.45887561638d+01, 0.51784792838d+01, 0.24256681992d+01,
     .        0.17503396740d+01, 0.55462309649d+01, 0.53654038849d+01,
     .        0.57480780172d+01, 0.30255378346d+01, 0.48885030466d+01,
     .        0.23804066375d+01, 0.44164487994d+01, 0.58749150929d+01,
     .        0.91211054980d+00, 0.12065228805d+00, 0.40327798040d+01,
     .        0.40409478753d+01, 0.14459834133d+01, 0.25196171527d+01,
     .        0.43656363145d+01, 0.27189892747d+01, 0.46383493041d+01,
     .        0.50853674937d+01, 0.38149646892d+01, 0.14500363887d+01,
     .        0.49143882553d+01, 0.45870791843d+01, 0.47260561516d+01,
     .        0.11319378162d+00, 0.21922693601d+01, 0.20357085573d-07,
     .        0.14636049305d+01, 0.13155120816d+01, 0.67084452009d+00,
c     DATA YPB0/                                                        
     .        0.17534552308d+01, 0.17103271183d+01, 0.16672159014d+01,
     .        0.66875228032d+00, 0.37413210846d+01, 0.40152318962d+01,
     .        0.40460100949d+01, 0.30243081942d+01, 0.13006685315d+00,
     .        0.49540856403d+00, 0.60738082984d+01, 0.14607222819d+01,
     .        0.31764033457d+01, 0.23395962205d+01, 0.56074501803d+00,
     .        0.21700665445d+01, 0.16242045858d+01, 0.53846060892d+01,
     .        0.13168439853d+01, 0.44410514348d+01, 0.53696172560d+01,
     .        0.50038845203d+01, 0.54536384501d+00, 0.60986528036d+01,
     .        0.40722372777d+01, 0.45229584426d+01, 0.32399050534d+01,
     .        0.28117072766d+01, 0.55320545254d+01, 0.42333318684d+01,
     .        0.40650872211d+01, 0.22653385542d+01, 0.24269452581d+01,
     .        0.58544659934d+01, 0.50437729855d+01, 0.28392608496d+01,
     .        0.47825017197d+01, 0.58783987653d+01, 0.62438688793d+01,
     .        0.10661535245d+01, 0.13307428252d+00, 0.74122751683d+00,
     .        0.13619009502d+01, 0.36597816104d+01, 0.42712877604d+01,
     .        0.18533266198d+01, 0.53798641353d+01, 0.38727392889d+01,
     .        0.58067319996d+01, 0.36361200155d+01, 0.21224568364d+01,
     .        0.29049608633d+01, 0.14798420908d+01, 0.57844745916d+01,
     .        0.20522386777d+01, 0.44072939918d+01, 0.40419439594d+01,
     .        0.37672244169d+01, 0.55451854448d+00, 0.24930650519d+01,
     .        0.41594136593d+01, 0.69395121474d+00, 0.17385633035d+00,
     .        0.23911660843d+01, 0.99543651257d+00, 0.23134689288d+01,
     .        0.26788181449d+01, 0.45292142641d+00, 0.61898981370d+01,
     .        0.13121937281d+01, 0.54965132385d+01, 0.53421363983d+01,
     .        0.31712025998d+01, 0.40025590706d+01, 0.18293721714d+01,
     .        0.36394922645d+01, 0.48127203488d+00, 0.23297476002d+01,
     .        0.14165685776d+01, 0.46352435951d+01, 0.28836026592d+01,
     .        0.47989197687d+01, 0.50151499836d+01, 0.36482082608d+01,
     .        0.31221201104d+01, 0.19051057066d+01, 0.13529440055d+01,
     .        0.30174582290d+01, 0.51972073964d+01, 0.62712828946d+01,
     .        0.14495357374d+01, 0.44076947137d+01, 0.24909830110d+01,
     .        0.10685604080d+01, 0.41627457086d+01, 0.50669289457d+01,
     .        0.50380011825d+01, 0.36069663304d+01, 0.63097656793d+00,
     .        0.85487159959d+00, 0.33123617750d+01, 0.39765977605d+01,
     .        0.14548364894d+01, 0.17629004249d+00, 0.59888458893d+01,
     .        0.45390285327d+01, 0.61058502709d+01, 0.24827966782d+01,
     .        0.42821353155d+01, 0.16878659519d+01, 0.24699974693d+01,
     .        0.24248666969d+01, 0.25734549410d+01, 0.40919809787d+01,
     .        0.27952781819d+01, 0.42891464724d+01, 0.30673155677d+01,
     .        0.35147174141d+01, 0.22437588075d+01, 0.20448129838d+00,
     .        0.30204280375d+01, 0.31555332815d+01, 0.37281960315d+01,
     .        0.48256769207d+01, 0.12593726357d+01, 0.62032019763d+01,
     .        0.60275647247d+01, 0.53816060415d+01, 0.d0,
c     DATA ZPB0/                                                        
     .        0.47694978870d+01, 0.19876827749d+01, 0.20315307235d+01,
     .        0.84186847842d+00, 0.56274362994d+01, 0.71009162348d+00,
     .        0.54510775534d+01, 0.23272042745d+01, 0.49803420100d+01,
     .        0.24450556426d+00, 0.61534101468d+01, 0.11782691215d+00,
     .        0.12663347326d+01, 0.52733797680d+01, 0.26000614231d+01,
     .        0.10080911141d+01, 0.34134496812d+01, 112*0.d0/
      data xpc0/
     .        0.62830758500d+01, 0.12566151700d+02, 0.18849227550d+02,
     .        0.83996847318d+02, 0.52969096509d+00, 0.21329909544d+00,
     .        0.10593819302d+01, 0.16728376159d+03,-0.62865989683d+01,
     .        0.62795527316d+01, 0.12036460735d+02, 0.14143495242d+02,
     .        0.10213285546d+02, 0.74781598567d-01, 0.38133035638d-01,
     .        0.52236939198d+01, 0.25132303400d+02, 0.68127668151d+01,
     .        0.57533848849d+01, 0.78604193924d+01, 0.63093741698d+01,
     .       -0.62567775302d+01, 0.66812248534d+01, 0.58849268466d+01,
     .        0.17789845620d+02, 0.42659819088d+00, 0.11506769770d+02,
     .       -0.23528661538d+01, 0.15773435424d+01,-0.47057323075d+01,
     .        0.12168002697d+02, 0.15613747598d+03, 0.11790629089d+02,
     .       -0.70585984613d+01,-0.71430695618d+02, 0.23942439025d+03,
     .        0.62831431603d+01,-0.62830085397d+01, 0.10977078805d+02,
     .       -0.70793738568d+01, 0.54867778432d+01, 0.46940029547d+01,
     .        0.11769853693d+02, 0.15890728953d+01, 0.88273902699d+01,
     .        0.25057067586d+03, 0.17260154655d+02,-0.53680451210d+00,
     .        0.52257741809d+00, 0.13367972631d+02, 0.94377629349d+01,
     .        0.18073704939d+02,-0.37387614301d+01, 0.12352852605d+02,
     .        0.11856218652d+02, 0.55075532387d+01, 0.63038512455d+01,
     .       -0.62623004545d+01, 0.90279923168d+02,-0.84672475845d+02,
     .        0.64963749454d+01, 0.60697767546d+01,-0.12569674818d+02,
     .        0.84292412665d+01,-0.22041264244d+00, 0.77713771468d+02,
     .        0.20618554844d+00,-0.62840561711d+01, 0.62820955289d+01,
     .        0.92255392733d+01, 0.18319536585d+02, 0.62901893970d+01,
     .       -0.77552261132d+00, 0.62759623030d+01, 0.64384962494d+01,
     .       -0.61276554506d+01, 0.12562628582d+02, 0.20426571092d+02,
     .        0.12559038153d+02, 0.11371704690d+02,-0.41369104335d+01,
     .        0.17298182327d+02, 0.14956319713d+00, 0.16496361396d+02,
     .       -0.39814900341d+00, 0.58564776591d+01,-0.54812549189d+01,
     .        0.13095842665d+02, 0.10447387840d+02, 0.95143132921d+02,
     .        0.63989728631d+00, 0.80310922631d+01, 0.21228392024d+02,
     .        0.15110466120d+02, 0.23543230505d+02, 0.70848967811d+01,
     .        0.50886288398d+01, 0.12139553509d+02, 0.32271130452d+03,
     .       -0.79629800682d+00, 0.24072921470d+02, 0.31546870849d+01,
     .        0.15720838785d+02, 0.70993304836d+00,-0.31283887651d+01,
     .        0.39302096962d+01, 0.41643119896d+01, 0.22003914635d+02,
     .       -0.74775228602d+01,-0.86359420038d+01, 0.14712317116d+02,
     .        0.14985440013d+03, 0.41948464388d+00,-0.10988808158d+02,
     .       -0.65147619768d+02,-0.45350594369d+01, 0.16100068574d+03,
     .        0.18422629359d+02, 0.18451078547d+02, 0.76329432597d+01,
     .        0.25158601720d+02, 0.10522683832d+01, 0.11624747044d+01,
     .        0.23314131440d+03, 0.25443144199d+01, 0.00000000000d+00,
     .        0.33406124267d+01, 0.73424577802d+01,-0.82576981221d+02,
c     DATA YPC0/                                                        
     .        0.62830758500d+01, 0.12566151700d+02, 0.18849227550d+02,
     .        0.83996847318d+02, 0.52969096509d+00, 0.21329909544d+00,
     .        0.10593819302d+01, 0.16728376159d+03,-0.62865989683d+01,
     .        0.62795527316d+01, 0.12036460735d+02, 0.14143495242d+02,
     .        0.10213285546d+02, 0.74781598567d-01, 0.52236939198d+01,
     .        0.38133035638d-01, 0.25132303400d+02, 0.68127668151d+01,
     .        0.57533848849d+01, 0.78604193924d+01, 0.63093741698d+01,
     .       -0.62567775302d+01, 0.66812248534d+01, 0.58849268466d+01,
     .        0.17789845620d+02, 0.11506769770d+02, 0.42659819088d+00,
     .       -0.23528661538d+01, 0.55075532387d+01, 0.15773435424d+01,
     .       -0.47057323075d+01, 0.12168002697d+02, 0.15613747598d+03,
     .        0.11790629089d+02,-0.70585984613d+01,-0.71430695618d+02,
     .        0.23942439025d+03,-0.62830085397d+01, 0.62831431603d+01,
     .       -0.70793738568d+01, 0.46940029547d+01, 0.94377629349d+01,
     .        0.54867778432d+01, 0.11769853693d+02, 0.15890728953d+01,
     .        0.88273902699d+01, 0.25057067586d+03, 0.52257741809d+00,
     .       -0.53680451210d+00, 0.17260154655d+02, 0.10977078805d+02,
     .        0.18073704939d+02,-0.37387614301d+01, 0.12352852605d+02,
     .        0.11856218652d+02, 0.63038512455d+01,-0.62623004545d+01,
     .        0.90279923168d+02,-0.84672475845d+02, 0.60697767546d+01,
     .        0.64963749454d+01, 0.77713771468d+02,-0.12569674818d+02,
     .       -0.22041264244d+00, 0.20618554844d+00,-0.62840561711d+01,
     .        0.62820955289d+01, 0.92255392733d+01, 0.18319536585d+02,
     .        0.62901893970d+01,-0.77552261132d+00, 0.62759623030d+01,
     .        0.84292412665d+01, 0.64384962494d+01, 0.70848967811d+01,
     .       -0.61276554506d+01, 0.12562628582d+02, 0.13367972631d+02,
     .        0.20426571092d+02, 0.12559038153d+02,-0.41369104335d+01,
     .        0.14956319713d+00, 0.11371704690d+02, 0.17298182327d+02,
     .        0.16496361396d+02,-0.39814900341d+00,-0.54812549189d+01,
     .        0.16730463690d+02, 0.13095842665d+02, 0.58564776591d+01,
     .        0.10447387840d+02, 0.95143132921d+02, 0.63989728631d+00,
     .        0.15110466120d+02, 0.15720838785d+02, 0.21228392024d+02,
     .        0.23543230505d+02, 0.12139553509d+02, 0.31546870849d+01,
     .        0.32271130452d+03,-0.79629800682d+00, 0.24072921470d+02,
     .        0.70993304836d+00,-0.31283887651d+01, 0.41643119896d+01,
     .        0.80310922631d+01, 0.41948464388d+00,-0.74775228602d+01,
     .        0.22003914635d+02,-0.86359420038d+01, 0.14985440013d+03,
     .        0.14712317116d+02, 0.50886288398d+01,-0.10988808158d+02,
     .       -0.65147619768d+02,-0.45350594369d+01, 0.16100068574d+03,
     .        0.18422629359d+02, 0.18451078547d+02, 0.25158601720d+02,
     .        0.10522683832d+01, 0.11624747044d+01, 0.25443144199d+01,
     .        0.23314131440d+03, 0.39302096962d+01, 0.33406124267d+01,
     .        0.73424577802d+01,-0.82576981221d+02, 0.d0,
c     DATA ZPC0/                                                        
     .        0.84334661581d+02, 0.52969096509d+00, 0.21329909544d+00,
     .        0.16762157585d+03, 0.71092881355d+02, 0.55075532387d+01,
     .        0.52236939198d+01, 0.10593819302d+01, 0.10213285546d+02,
     .        0.15647529025d+03, 0.38133035638d-01, 0.14143495242d+02,
     .        0.42659819088d+00, 0.94377629349d+01, 0.23976220452d+03,
     .       -0.23528661538d+01, 0.62830758500d+01, 112*0.d0/
      data xpa1/
     .        0.64715245935d-05, 0.24328941087d-06, 0.67123298803d-07,
     .        0.13359689914d-07, 0.13356173606d-07,
c     DATA YPA1/                                                        
     .        0.64723354738d-05, 0.24330318905d-06, 0.29169086929d-07,
     .        0.13360827358d-07, 0.13356173911d-07,
c     DATA ZPA1/                                                        
     .        0.14314405063d-04, 0.23915560086d-06, 3*0.d0/
      data xpb1/
     .        0.12902739059d+01, 0.12470437472d+01, 0.35864076689d+01,
     .        0.60806812782d+01, 0.33045975792d+01,
c     DATA YPB1/                                                        
     .        0.60026015312d+01, 0.59594032932d+01, 0.11146499880d+01,
     .        0.13683837257d+01, 0.17338012435d+01,
c     DATA ZPB1/                                                        
     .        0.49845236384d+01, 0.49414141743d+01, 3*0.d0/
      data xpc1/
     .        0.12566151700d+02, 0.18849227550d+02, 0.62830758500d+01,
     .       -0.62865989683d+01, 0.62795527316d+01,
c     DATA YPC1/                                                        
     .        0.12566151700d+02, 0.18849227550d+02, 0.62830758500d+01,
     .       -0.62865989683d+01, 0.62795527316d+01,
c     DATA ZPC1/                                                        
     .        0.62830758500d+01, 0.12566151700d+02, 3*0.d0/
      data xpa2/
     .        0.27339819907d-09,
c     DATA YPA2/                                                        
     .        0.27368979976d-09,
c     DATA ZPA2/                                                        
     .        0.61084625090d-09/
      data xpb2/
     .        0.59707943161d+01,
c     DATA YPB2/                                                        
     .        0.44003712823d+01,
c     DATA ZPB2/                                                        
     .        0.43995036104d+00/
      data xpc2/
     .        0.12566151700d+02,
c     DATA YPC2/                                                        
     .        0.12566151700d+02,
c     DATA ZPC2/                                                        
     .        0.62830758500d+01/
c**                                                                     
      t=(dj-dj0)/365.25d0
C      if(abs(t).ge.101) then
C        write(6,1300) t+2000
C1300    format(1x,'DATE',f9.2,' EN DEHORS DE L''INTERVALLE 1900-2100')
C        stop 2222
C      endif
c**                                                                     
      do 1 j=1,3
        xyzp(j)=0.d0
        do 2 k=1,nxyz(1,j)
          xyzp(j)=xyzp(j)+xpa0(k,j)*cos(xpb0(k,j)+xpc0(k,j)*t)
2       continue
        do 3 k=1,nxyz(2,j)
          xyzp(j)=xyzp(j)+xpa1(k,j)*t*cos(xpb1(k,j)+xpc1(k,j)*t)
3       continue
        do 4 k=1,nxyz(3,j)
          xyzp(j)=xyzp(j)+xpa2(k,j)*t*t*cos(xpb2(k,j)+xpc2(k,j)*t)
4       continue
1     continue
c                                                                       
CALCUL DES COORDONNEES EQUATORIALES MOYENNES J2000                      
c                                                                       
      yy=xyzp(2)
      zz=xyzp(3)
      xyzp(2)=yy*cose-zz*sine
      xyzp(3)=yy*sine+zz*cose
c                                                                       
c  calcul des coordonnees equatoriales de la date                       
c                                                                       
c  dmat est la matrice de precession qui fait passer des coordonnees    
c  equatoriales j2000 aux coordonnees equatoriales de la date; elle est
c  calculee ici a la precision de 3.d-7 sur l'intervalle (1900,2100).  
c 
      dmat(1,1)=1.d0-297.202d-10*t**2                                  
      dmat(1,2)=-22.36049d-5*t-6.775d-10*t**2                          
      dmat(1,3)= -9.71665d-5*t+2.068d-10*t**2                          
      dmat(2,1)= -dmat(1,2)                                            
      dmat(2,2)=1.d0-249.996d-10*t**2                                
      dmat(2,3)=    -108.634d-10*t**2                                  
      dmat(3,1)= -dmat(1,3)                                            
      dmat(3,2)=  dmat(2,3)                                            
      dmat(3,3)=1.d0 -47.206d-10*t**2                                  
*                                                                      
      do 10 i=1,3                                                      
        xyzpdat(i)=0.d0                                               
        do 11 j=1,3                                                    
          xyzpdat(i)=xyzpdat(i)+dmat(i,j)*xyzp(j)                      
11      continue                                             
10    continue     
      return
      end
