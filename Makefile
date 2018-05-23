help:
	@echo 'Makefile for a web-bot deploy                                   '
	@echo '                                                                '
	@echo 'Usage:                                                          '
	@echo '   make dep                       ansible deploy                '

dep:
	ansible-playbook -v ./service_run.ansible
