
������
------
�������� �� ������ ������. ����� ����� ������ ��� http://basmp.narod.ru

������ �������: ��� ��� ����������, ��� ��������-��������-��������. �������� ���

��� ������� �� ������. �� ������ �� �������



��� ���������
-------------
������������� ��� ����� ������ ��������. ��

m syncdb

(�� �������� ������� ������)

����������� � �����

m runserver

�� ������� �������� �������� ������ �������.

-------------
���������� � ������ 1.2 �� ������ 1.0, ������ ��������� ��� ������, ��� �� ����� ���� � �� ��������

(��������) ����� 2010 - ������ 2011 (���� ������ ����)



----------------------
��������� ���������

���� agd/config

config.py  - ��������� � ����. ���� ��������� � ��������� ����� �������

commands.txt  - ������� (� ��������) ������� �����������. �������� ��� ������
py_commands.py - ��������� ����� �������
default.txt  - ����� ���������� ������� �� �������

��� ��������� - ��������� ������. � ������ ������ ������ colorise.txt


������� � �������� �������� �������� ����������. ����� �� ���������
--------------------------------

������� �������
---------------

���������
---------
\~       - ������
\dots    - ���������
\<-
\->
\<->
\(c)
\TeX     - ���� TeX
(������ �������� � ������� - �������)


������� ���� \<�������> { <� ���� �����������> }
------------------------------------
\b       
\i
\s

\'
\"

\sub
\sup


\img
\imgc
\imgl0
\imgl
\imgr0
\imgr

\raw
\code

\par        - (����.) ��������
\first_par  - (����.) �������� � ��������


������ ���������. ��� �������
-----------------------------
\title      - ��������� ��������
\subtitle

\h1         - ���������
\h2

\as_is
\note
\warning
\tip


������� �������
---------------
\code_box_begin
 <...>
\code_box_end


\url { <�����> }
 <���>
\endurl


�������
-------
\table { <���> }       - ��� �� ����.
\header{ <��� �������> }{...} ... {...} - ���������. (����.) ���� �������� �� �� ���-��
\align{ <>.- }                          - ������������. (����.) �� �� ���-�� ��������. 
                                            '<' - �����, 
                                            '>' - ������, 
                                            '.' - �����, 
                                            '-' - �� ������
\row{...}{...} ... {...}                - ���. 
...
\row{...}{...} ... {...}
\endtable


������
------
\var { \���1, ... , \���N }
\let { ���������1, ... , ���������N }
\if { ���������B } ���������T \else ���������F \endif
\for { ���������1 , ... , ���������N ; ���������B ; ���������1 , ... , ���������N } ... \endfor
\def{ \��� } ... \enddef           -    �������

���������
---------
\��� - ����������
=    - �����
+   
-
* 
/
<
>
==
( ... )
" ... "
' ... '
����� ����� � �������

��� ���������� ��� ����� \let ������ ��������� �� �������� � �����


���
---
��������� ����������� ����������� ��������� ������ (������ 
\import{colorise} 

������������ ��������

\code_colorise{ <��� �����> }{ <���> }

���� ����������

\cpp{ <���> }
\asm{ <���> }
)

����� �������� ������� � �������� �����

��������� ������ ������� � ���������, ��������, ������������ \itemize � \enumerate

�������, ������� ����� ����� ���������. �����, ����������� ��������� � ����������� ������.

��������� ����������� ������� �� ����������� ������� � �� ������. ������� \import . ���� ���� ������ 'colorise'



������� �������� � ���8
