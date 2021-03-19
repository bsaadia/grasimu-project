c**********************************************************************
c* das programm ranmedi erzeugt fluktuationen, die durch verschie-    *
c* dene autokorrelationsfunktionen charakterisiert sind.              *
c*                                                                    *
c* gauss-akf (1)                                                      *
c* exponentielle akf (2)                                              *
c* mittelwertfreie exponential-akf (3)                                *
c* anisotrope akf (4)                                                 *
c* von karman akf (5)                                                 *
c*                                                                    *
c* a und b sind die korrelationslaengen in x-, bzw. z-richtung. die   *
c* fluktuation wird fuer ein gitter von 1024 x 1024   punkten berechnet *
c* die varianz der fluktuationen ist auf 1 normiert. das feld fluk    *
c* muss noch mit der standardabweichung multipliziert werden          *
c* eingabefile ist ../randinq                                   *
c* ausgabefile ist ../rando                                        * 
c*                                                                    * 
c* michael roth  15.04.1993                                           *
c*  geaendert von alex am 7.7.93
c* edited by benjamin saadia 06.14.2020                                                                  *
c**********************************************************************
c
      subroutine mainfunc()
      parameter (lx=1024,lz=1024)
      complex fluk(lx,lz),carg
      integer*8 lxx,lzz,idum
!f2py intent(out) fluk
      save idum
c  CHANGE THIS TO YOUR PATH XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
c     home='/home/bsaadia/Code/GG_CRM_UAV/Alex/'
      open (unit=10,file='rando',form='unformatted')
c      open (unit=10,file=home//'rando')
      open (unit=11,file='randinq')
1     continue
c-----art der und parameter der autokorrelationsfunktion------
      read (11,*)
      read(11,*) antw
      read (11,*)
      if (antw.eq.4) then
        read(11,*) a,b
      else
        read(11,*) a
      endif
      read (11,*)
      read(11,*) idum
      write(*,*)'idum = ',idum
      read(11,*)lxx,lzz
c
      if (antw.eq.1.) then
        call sub1(fluk,a,lx,lz)
      else if (antw.eq.2.) then
        call sub2(fluk,a,lx,lz)
      else if (antw.eq.3.) then
        call sub3(fluk,a,lx,lz)
      else if (antw.eq.4.) then
        call sub4(fluk,a,b,lx,lz)
      else if (antw.eq.5.) then
        call sub5(fluk,a,lx,lz)
      else
        goto 1
      endif
c
      pi=3.141592654
      do 200 i=2,lx/2
        do 250 j=2,lz
          zu=zuf(idum)
          carg=cexp(cmplx(0.0,2.*pi*(zu-0.5)))
          if (j.eq.lz/2+1) carg = (1.0,0.0)
          fluk(i,j)=fluk(i,j)*carg
          fluk(lx+2-i,lz+2-j)=conjg(fluk(i,j))
250     continue
200   continue
c
      do 300 j = 2,lz/2
        zu=zuf(idum)
        carg=cexp(cmplx(0.0,2.*pi*(zu-0.5)))
        fluk(1,j)=fluk(1,j)*carg
        fluk(1,lz+2-j)=conjg(fluk(1,j))
        zu=zuf(idum)
        carg=cexp(cmplx(0.0,2.*pi*(zu-0.5)))
        fluk(j,1)=fluk(j,1)*carg
        fluk(lx+2-j,1)=conjg(fluk(j,1))
300   continue
c
      call f2(lx,lz,fluk,1.)
c
      do 400 j=1,lz
c	do 450 i=1,lx
      write(10) (real(fluk(i,j)),i=1,lx)
c450	continue
400   continue
c
c      call clockv(g1,g2,0,2)
c      write(*,*) g1,g2
      close(10)
c      stop
      end
      end program
c
      subroutine sub1(fluk,a,lx,lz)
      complex fluk(lx,lz)
      real kx,kz,kr2
      pi=3.141592654
      kx=2.*pi/float(lx)
      kz=2.*pi/float(lz)
      do 100 i=1,lx/2+1
        do 150 j=1,lz/2+1
          kr2=(float(i-1)*kx)**2+(float(j-1)*kz)**2
          x=pi*a*a*exp(-kr2*a*a/4.)
          fluk(i,j)=cmplx(sqrt(x),0.0)
150     continue
          do 170 j=1,lz/2
            fluk(i,lz+1-j)=fluk(i,j+1)
170       continue
100   continue
      end
c
c
      subroutine sub2(fluk,a,lx,lz)
      complex fluk(lx,lz)
      real kx,kz,kr2
      pi=3.141592654
      kx=2.*pi/float(lx)
      kz=2.*pi/float(lz)
      do 100 i=1,lx/2+1
        do 150 j=1,lz/2+1
          kr2=(float(i-1)*kx)**2+(float(j-1)*kz)**2
          x=2*pi*a**2
          z=(1.+kr2*a**2)**1.5
          fluk(i,j)=cmplx(sqrt(x/z),0.0)
150     continue
          do 170 j=1,lz/2
            fluk(i,lz+1-j)=fluk(i,j+1)
170       continue
100   continue
      end
c
c
      subroutine sub3(fluk,a,lx,lz)
      complex fluk(lx,lz)
      real kx,kz,kr2
      pi=3.141592654
      kx=2.*pi/float(lx)
      kz=2.*pi/float(lz)
      do 100 i=1,lx/2+1
        do 150 j=1,lz/2+1
          kr2=(float(i-1)*kx)**2+(float(j-1)*kz)**2
          x=2.*pi*a**4.*kr2*(3.5+kr2*a*a)
          z=(1.+kr2*a**2)**1.5*(1+kr2*a*a)**2.
          fluk(i,j)=cmplx(sqrt(x/z),0.0)
150     continue
          do 170 j=1,lz/2
            fluk(i,lz+1-j)=fluk(i,j+1)
170       continue
100   continue
      end
c
c
      subroutine sub4(fluk,a,b,lx,lz)
      complex fluk(lx,lz)
      real kx,kz
      pi=3.141592654
      kx=2.*pi/float(lx)
      kz=2.*pi/float(lz)
      do 100 i=1,lx/2+1
        do 150 j=1,lz/2+1
          x=4.*a*b
          z=(1.+(a*(i-1.)*kx)**2)*(1.+(b*(j-1.)*kz)**2)
          fluk(i,j)=cmplx(sqrt(x/z),0.0)
150     continue
          do 170 j=1,lz/2
            fluk(i,lz+1-j)=fluk(i,j+1)
170       continue
100   continue
      end
c
c
      subroutine sub5(fluk,a,lx,lz)
      complex fluk(lx,lz)
      real kx,kz,kr2
      pi=3.141592654
      kx=2.*pi/float(lx)
      kz=2.*pi/float(lz)
      do 100 i=1,lx/2+1
        do 150 j=1,lz/2+1
          kr2=(float(i-1)*kx)**2+(float(j-1)*kz)**2
          x=2.*pi*a*a
          z=1.+kr2*a*a
          fluk(i,j)=cmplx(sqrt(x/z),0.0)
150     continue
          do 170 j=1,lz/2
            fluk(i,lz+1-j)=fluk(i,j+1)
170       continue
100   continue
      end
c
c
      function zuf(idum)
c*
c**************************************************
c*                                                *
c*     zufallszahlengenerator aus                 *
c*     "numerical recipes"                        *
c*     periode praktisch unendlich                *
c*                                                *
c*     beim aufruf muss der startwert             *
c*     idum integer und kleiner 0 sein            *
c*                                                *
c**************************************************
c*
      parameter (m=714025,ia=1366,ic=150889,rm=1./m)
      dimension ir(97)
      integer*8 idum,iff,iy,j
      save
      data iff /0/
      if (idum.lt.0.or.iff.eq.0) then
c          initialisierung
         iff=1
         idum=mod(ic-idum,m)
         do 11 j=1,97
            idum=mod(ia*idum+ic,m)
            ir(j)=idum
 11      continue
         idum=mod(ia*idum+ic,m)
         iy=idum
      endif
c
      j=1+(97*iy)/m
      if(j.gt.97.or.j.lt.1) then
         write(*,*)' ZUF: fehler: j =',j,idum
         stop
      end if
      iy=ir(j)
      zuf=iy*rm
      idum=mod(ia*idum+ic,m)
      ir(j)=idum
      return
      end
c**************************************************
c* unterprogramm f2 berechnet die 2 dim.          *
c* fouriertransformation fuer ein 1024 x 1024 feld*
c* ckar = komplexes 2 dim. feld                   *
c* signi = -1. fouriertransformation              *
c* signi = 1. inv. fouriertransformation          *
c**************************************************
      subroutine f2(lx,lz,ckar,signi)
      parameter(ll=1024,llz=1024)
      complex ckar(ll,llz),cz(llz),cx(ll)
c
      do 300 i=1,lx
        do 350 j=1,lz
          cz(j)=ckar(i,j)
350     continue
        call fork(lz,cz,signi)
c
        do 370 j=1,lz
          ckar(i,j)=cz(j)
370    continue
c
300   continue
c
      do 400 j=1,lz
        do 450 i=1,lx
          cx(i)=ckar(i,j)
450     continue
        call fork(lx,cx,signi)
c
        do 470 i=1,lx
          ckar(i,j)=cx(i)
470     continue
c
400   continue
c
      end
      subroutine fork(lx,cx,signi)
      complex cx(lx),carg,cw,ctemp
      pi=3.14159265
      j=1
      sc=1./float(lx)
      sc=sqrt(sc)
      do 5 i=1,lx
        if (i.gt.j) goto 2
        ctemp=cx(j)*sc
        cx(j)=cx(i)*sc
        cx(i)=ctemp
2       m=lx/2
3       if (j.le.m) goto 5
        j=j-m
        m=m/2
        if (m.ge.1) goto 3
5     j=j+m
      l=1
6     istep=2*l
      do 8 m=1,l
        carg=cmplx(0.,1.)*(pi*signi*float(m-1)/float(l))
        cw=cexp(carg)
        do 8 i=m,lx,istep
          ctemp=cw*cx(i+l)
          cx(i+l)=cx(i)-ctemp
8     cx(i)=cx(i)+ctemp
      l=istep
      if (l.lt.lx) goto 6
      return
      end
