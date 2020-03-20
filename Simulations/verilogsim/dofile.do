add wave -position insertpoint  \
sim/:tb_covid19:A \
sim/:tb_covid19:initdone \
sim/:tb_covid19:clock \
sim/:tb_covid19:Z \

run -all
