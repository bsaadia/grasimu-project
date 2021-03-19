**********************************************************************
* das programm ranmedi erzeugt fluktuationen, die durch verschie-    *
* dene autokorrelationsfunktionen charakterisiert sind.              *
*                                                                    *
**********************************************************************

      subroutine bin2asc()
      parameter (lx=1024,lz=1024)
c      character home*35
	integer*8 lxx,lzz,idum
	real fluk(lx,lz)
	save idum
c  CHANGE THIS TO YOUR PATH
c      home='/home/bsaadia/Code/GG_CRM_UAV/Alex/'
      open (unit=10,file='rando',form='unformatted')
      open (unit=11,file='randout')
      do 400 j=1,lz
c	do 450 i=1,lx
      read(10) (fluk(i,j),i=1,lx)
c450	continue
400   continue
	do 500 j=1,lz
       do 550 i=1,lx
      write(11,*) i,j,fluk(i,j)
550    continue
500   continue
	close(10)
	close(11)
      end
      end program
