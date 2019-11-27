C*******************************************************************
C  Subroutine FITGAUS.F  -Fit par une gaussienne-  Bouchy 03/2002
C
C  Inputs: x(ndata)  
C	   y(ndata)  
C	   wei(ndata)		poids (inverse ind. stand. dev.)
C	   a(m)			coefficients (initial guess) 
C
C  Outputs: a(m)		coefficients
C	    siga(m)		incertitude sur coefficients
C	    f(ndata)		valeur de la fonction
C
C  Fit non lineaire d'une gaussienne a 4 parametres par la methode 
C  de Levenberg-Marquardt. Utilise les subroutines MRQMIN, MRQCOF, 
C  COVSRT et GAUSSJ.
C
C	f(x) = a1 * exp( -(x-a2)**2 / (2*a3**2) ) + a4
C
C
C   2004-02-23  Correction bug iteration
C******************************************************************
	
      SUBROUTINE fitgaus(x,y,wei,ndata,m,a,siga,f)
      
      INTEGER m,ndata,i,j,mmax,nmax,cpt
      PARAMETER (nmax=10000,mmax=4)
      DOUBLE PRECISION x(ndata),y(ndata),wei(ndata),f(ndata)
      DOUBLE PRECISION a(m),siga(m)      
      DOUBLE PRECISION alpha(mmax,mmax),covar(mmax,mmax),sig(nmax)
      DOUBLE PRECISION alamda,chisq,alamda0,arg,ex

Cf2py intent(in) ndata
Cf2py intent(in) depend(ndata) x
Cf2py intent(in) depend(ndata) y
Cf2py intent(in) depend(ndata) wei
Cf2py intent(in) m
Cf2py intent(in,out) depend(m) a
Cf2py intent(in,out) depend(m) siga
Cf2py intent(in,out) depend(ndata) f

	do i=1,ndata
	  sig(i)=1/wei(i)
	enddo

C************ premiere iteration *********************	
	alamda=-1.
	call mrqmin(x,y,sig,ndata,a,m,covar,alpha,chisq,alamda)
	
	alamda0=1.e-8
	cpt=0
C************** Iteration jusqu'a convergence *************	
	do while ((alamda.gt.alamda0).and.(cpt.lt.100))
	  
	  cpt=cpt+1
	  call mrqmin(x,y,sig,ndata,a,m,covar,alpha,chisq,alamda)
	  
	enddo
C************** derniere iteration pour calcul des erreurs *********	
	alamda=0.
	call mrqmin(x,y,sig,ndata,a,m,covar,alpha,chisq,alamda)
	if (ndata.gt.4) then
		nfree=ndata-4
	else
		nfree=ndata
	endif
	do j=1,m
	   siga(j)=sqrt(covar(j,j))*sqrt(chisq/nfree)
	enddo
	
	do i=1,ndata
           arg=(x(i)-a(2))/a(3)
           ex=exp(-(arg**2)/2.)
           f(i)=a(1)*ex+a(4)	
	enddo
	
	
	end


      SUBROUTINE funcs(x,a,y,dyda,ma)
      INTEGER ma,mmax
      PARAMETER (mmax=4)
      DOUBLE PRECISION x,y,a(ma),dyda(mmax),arg,ex
C     y = a1*exp(-(x-a2)^2/(2*a3^2)) + a4
      arg=(x-a(2))/a(3)
      ex=exp(-(arg**2)/2.)
      y=a(1)*ex+a(4)	
      dyda(1)=ex
      dyda(2)=a(1)*ex*arg/a(3)
      dyda(3)=a(1)*ex*arg**2/a(3)
      dyda(4)=1.
      return
      END      	
		
      SUBROUTINE mrqmin(x,y,sig,ndata,a,ma,covar,alpha,chisq,alamda)
      INTEGER ma,ndata,nmax,mmax,j,k,l
      PARAMETER (nmax=10000,mmax=4)
      DOUBLE PRECISION alamda,chisq,ochisq
      DOUBLE PRECISION a(ma),x(ndata),y(ndata),sig(nmax)
      DOUBLE PRECISION alpha(mmax,mmax),covar(mmax,mmax)      
      DOUBLE PRECISION atry(mmax),beta(mmax),da(mmax)
      SAVE ochisq,atry,beta,da
      if(alamda.lt.0.)then
        alamda=0.001
        call mrqcof(x,y,sig,ndata,a,ma,alpha,beta,chisq)
        ochisq=chisq
        do j=1,ma
          atry(j)=a(j)
        enddo
      endif
      do j=1,ma
        do k=1,ma
          covar(j,k)=alpha(j,k)
        enddo
        covar(j,j)=alpha(j,j)*(1.+alamda)
        da(j)=beta(j)
      enddo
      call gaussj(covar,ma,da,1,1)
      if(alamda.eq.0.)then
        call covsrt(covar,ma)
        return
      endif
      j=0
      do l=1,ma
        atry(l)=a(l)+da(l)
      enddo
      call mrqcof(x,y,sig,ndata,atry,ma,covar,da,chisq)
      if (chisq.lt.ochisq) then
        alamda=0.1*alamda
        ochisq=chisq
        do j=1,ma
          do k=1,ma
            alpha(j,k)=covar(j,k)
          enddo
          beta(j)=da(j)
        enddo
        do l=1,ma
          a(l)=atry(l)
        enddo
      else
        alamda=10.*alamda
        chisq=ochisq
      endif
      return
      END
	
      SUBROUTINE covsrt(covar,ma)
      INTEGER ma,mmax,i,j,k
      PARAMETER (mmax=4)
      DOUBLE PRECISION covar(mmax,mmax),swap
c      do i=ma+1,ma
c        do j=1,i
c          covar(i,j)=0.
c          covar(j,i)=0.
c	enddo
c      enddo	
      k=ma
      do j=ma,1,-1
          do i=1,ma
            swap=covar(i,k)
            covar(i,k)=covar(i,j)
            covar(i,j)=swap
	  enddo
          do i=1,ma
            swap=covar(k,i)
            covar(k,i)=covar(j,i)
            covar(j,i)=swap
	  enddo
          k=k-1
      enddo	
      return
      END

      SUBROUTINE gaussj(a,n,b,m,mp)
      INTEGER m,mp,n,mmax
      PARAMETER (mmax=4)
      DOUBLE PRECISION a(mmax,mmax),b(mmax,mmax)
      INTEGER i,icol,irow,j,k,l,ll,indxc(mmax),indxr(mmax),ipiv(mmax)
      DOUBLE PRECISION big,dum,pivinv
      do j=1,n
        ipiv(j)=0
      enddo
      do i=1,n
        big=0.
        do j=1,n
          if(ipiv(j).ne.1)then
            do k=1,n
              if (ipiv(k).eq.0) then
                if (abs(a(j,k)).ge.big)then
                  big=abs(a(j,k))
                  irow=j
                  icol=k
                endif
c              else if (ipiv(k).gt.1) then
c                pause 'singular matrix in gaussj'
              endif
	    enddo
          endif
	enddo
        ipiv(icol)=ipiv(icol)+1
        if (irow.ne.icol) then
          do l=1,n
            dum=a(irow,l)
            a(irow,l)=a(icol,l)
            a(icol,l)=dum
	  enddo 
          do l=1,m
            dum=b(irow,l)
            b(irow,l)=b(icol,l)
            b(icol,l)=dum
	  enddo 
        endif
        indxr(i)=irow
        indxc(i)=icol
c        if (a(icol,icol).eq.0.) pause 'singular matrix in gaussj'
        pivinv=1./a(icol,icol)
        a(icol,icol)=1.
        do l=1,n
          a(icol,l)=a(icol,l)*pivinv
	enddo
        do l=1,m
          b(icol,l)=b(icol,l)*pivinv
	enddo
        do ll=1,n
          if(ll.ne.icol)then
            dum=a(ll,icol)
            a(ll,icol)=0.
            do l=1,n
              a(ll,l)=a(ll,l)-a(icol,l)*dum
	    enddo
            do l=1,m
              b(ll,l)=b(ll,l)-b(icol,l)*dum
	    enddo
          endif
	enddo
      enddo	
      do l=n,1,-1
        if(indxr(l).ne.indxc(l))then
          do k=1,n
            dum=a(k,indxr(l))
            a(k,indxr(l))=a(k,indxc(l))
            a(k,indxc(l))=dum
	  enddo
        endif
      enddo	
      return
      END

      SUBROUTINE mrqcof(x,y,sig,ndata,a,ma,alpha,beta,chisq)
      INTEGER ma,ndata,mmax,nmax,i,j,k,l,m
      PARAMETER (mmax=4,nmax=10000)
      DOUBLE PRECISION a(ma),y(ndata),x(ndata),sig(nmax)
      DOUBLE PRECISION alpha(mmax,mmax),beta(mmax),dyda(mmax)
      DOUBLE PRECISION chisq,dy,sig2i,wt,ymod
      do j=1,ma
        do k=1,j
          alpha(j,k)=0.
	enddo
        beta(j)=0.
      enddo
      chisq=0.
      do i=1,ndata
        call funcs(x(i),a,ymod,dyda,ma)
        sig2i=1./(sig(i)*sig(i))
        dy=y(i)-ymod
        j=0
        do l=1,ma
            j=j+1
            wt=dyda(l)*sig2i
            k=0
            do m=1,l
                k=k+1
                alpha(j,k)=alpha(j,k)+wt*dyda(m)
 	    enddo
            beta(j)=beta(j)+dy*wt
	enddo
        chisq=chisq+dy*dy*sig2i
      enddo
      do j=2,ma
        do k=1,j-1
          alpha(k,j)=alpha(j,k)
	enddo
      enddo
      return
      END


