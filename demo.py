from mathai import *
question_list = """integrate(tan(x)/(sec(x)+tan(x)),x)
integrate(sec(x)/(sec(x)+tan(x)),x)
integrate(e^arctan(x)/(1+x^2),x)
integrate(sin(x)^2/(1+cos(x)),x)
integrate(tan(x)^3,x)
integrate(cos(x)/(1+cos(x)),x)
integrate(1/(1+sin(x)),x)
integrate(cos(x)/(1+sin(x))^2,x)
(x-1)^2 = x^2 - 1
(sin(x)+cosec(x))^2+(cos(x)+sec(x))^2=7+tan(x)^2+cot(x)^2
2*x/(2*x^2+5*x+2)>1/(x+1)
(5*x-1)<(x+1)^2&(x+1)^2<7*x-3
abs(x+5)*x+2*abs(x+7)-2=0
x*abs(x)-5*abs(x+2)+6=0
abs(3*x-5)+abs(8-x)=abs(3+2*x)
abs(x^2+5*x+9)<abs(x^2+2*x+2)+abs(3*x+7)
(A-B)|(B-A) <-> (A|B)-(A&B)
(cosec(x)-cot(x))^2=(1-cos(x))/(1+cos(x))
x^2 = 4 & x+y^2 = 1
x + y*x = 5 & y + z=5 & z = 4
integrate(abs(x+1),x,-4,10)
integrate(abs(sin(x)),x,-pi,pi/6)
x^(2*x)=1
-i*(i+1)^5
sqrt(x) = x-2
integrate(sin(x+a)/sin(x),x)
integrate(sqrt(sin(2*x))*cos(2*x),x)
x = y & y = z & x+y+z=180
sec(x)^2*tan(y)+sec(y)^2*tan(x)*dif(y,x)=0
x + y = 10 & x*y = 24
(x+y)*dif(y,x)=1
abs(abs(x-2)-3)<=2
abs(x)>=0
dif(y,x)=arcsin(x)
integrate(sin(x)^6+cos(x)^6+3*sin(x)^2*cos(x)^2,x)
integrate((x^4+x^2+1)/(x^2-x+1),x)
integrate(1/(sin(x)^2*cos(x)^2),x)
integrate(x/sqrt(x+4),x)
integrate(sin(x)^4,x)
integrate(2*x/(1+x^2),x)
integrate(sin(2*x+5)^2,x)
integrate(sqrt(a*x+b),x)
integrate(x*sqrt(x),x)
integrate(x*sqrt(1+2*x^2),x)
integrate(e^(2*x+3),x)
integrate(x/e^(x^2),x)
integrate(sin(x)*sin(cos(x)),x)
integrate(sin(3*x)*cos(4*x),x)
integrate(cos(2*x)*cos(4*x)*cos(6*x),x)
integrate(sin(2*x+1)^3,x)
integrate(sin(x)^3*cos(x)^3,x)
integrate(sin(x)*sin(2*x)*sin(3*x),x)
integrate(sin(4*x)*sin(8*x),x)
integrate(cos(2*x)^4,x)
integrate(x/((x+1)*(x+2)),x)
integrate(1/(x^2-9),x)
integrate((3*x-1)/((x-1)*(x-2)*(x-3)),x)
integrate(x/((x-1)*(x-2)*(x-3)),x)
integrate(2*x/(x^2+3*x+2),x)
integrate((1-x^2)/(x*(1-2*x)),x)
integrate(x/((x-1)^2*(x+2)),x)
integrate((2*x-3)/((x^2-1)*(2*x+3)),x)
integrate(5*x/((x+1)*(x^2-4)),x)
(x+2)*(x+3)/((x-2)*(x-3))<=1
cos(x)/(1+sin(x))+(1+sin(x))/cos(x)=2*sec(x)
tan(x)/(1-cot(x))+cot(x)/(1-tan(x))=1+sec(x)*cosec(x)
(1+sec(x))/sec(x)=sin(x)^2/(1-cos(x))
(cos(x)-sin(x)+1)/(cos(x)+sin(x)-1)=cosec(x)+cot(x)
integrate(x/((x-1)*(x^2+1)),x)
(sin(x)-2*sin(x)^3)/(2*cos(x)^3-cos(x))=tan(x)
(cosec(x)-sin(x))*(sec(x)-cos(x))=1/(tan(x)+cot(x))
integrate(2/((1-x)*(1+x^2)),x)
x^2-abs(x+2)+x>0
limit(sin(x)/x,x)
limit((x^2 - 1)/(x-1),x,1)
dif(y,x)=sqrt(4-y^2)
dif(y,x)+y=1
x^5*dif(y,x)=-y^5
dif(y,x)=(1+x^2)*(1+y^2)
x*(x^2-1)*dif(y,x)=1
(x^2+x*y)*dif(y,x)=(x^2+y^2)
dif(y,x)=(x+y)/x
(x-y)*dif(y,x)-(x+y)=0
(x^2-y^2)+2*x*y*dif(y,x)=0
x*dif(y,x)-y+x*sin(y/x)=0
(a+b)^2 = a^2 + b^2 + 2*a*b
(x-1)*(x+1) = x^2 - 1
integrate((7^(7^(7^x)))*(7^(7^x))*(7^x),x)"""
for item in question_list.split("\n"):
  god(item)
