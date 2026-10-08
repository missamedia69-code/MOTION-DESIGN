# MOTION-DESIGN — automatisations
# make help pour la liste des cibles

MD := ./md

.PHONY: help doctor new render preview inventory install fonts presets list clean bootstrap

help: ## Affiche cette aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

bootstrap: ## Installe TOUT (Python + Node + ffmpeg/ffprobe + Chromium)
	bash scripts/bootstrap.sh

doctor: ## Diagnostic complet du moteur
	$(MD) doctor

new: ## Créer un projet : make new NAME=ma-video CANVAS=9x16 [TEMPLATE=base|story]
	@test -n "$(NAME)" || (echo "Usage : make new NAME=ma-video CANVAS=9x16" && exit 1)
	$(MD) new $(NAME) --canvas $(or $(CANVAS),16x9) --template $(or $(TEMPLATE),base)

render: ## Rendre un projet : make render P=ma-video [PRESET=mp4-hq]
	@test -n "$(P)" || (echo "Usage : make render P=ma-video [PRESET=gif]" && exit 1)
	$(MD) render $(P) $(if $(PRESET),--preset $(PRESET),)

preview: ## Serveur de prévisualisation des sorties (port 8080)
	$(MD) preview --port $(or $(PORT),8080)

inventory: ## Régénère l'inventaire de assets/
	$(MD) inventory

install: ## Installer un élément : make install F=~/telechargements/logo.png
	@test -n "$(F)" || (echo "Usage : make install F=chemin/ou/url" && exit 1)
	$(MD) install $(F)

fonts: ## Liste des polices disponibles
	$(MD) fonts

presets: ## Liste des formats, exports et transitions
	$(MD) presets

list: ## Liste des projets
	$(MD) list

clean: ## Nettoie les intermédiaires : make clean P=ma-video
	@test -n "$(P)" || (echo "Usage : make clean P=ma-video" && exit 1)
	$(MD) clean $(P)

hf-check: ## Contrôle un projet HyperFrames : make hf-check P=hf-demo
	@test -n "$(P)" || (echo "Usage : make hf-check P=hf-demo" && exit 1)
	./scripts/hf check projects/$(P)

hf-render: ## Rend un projet HyperFrames : make hf-render P=hf-demo [Q=draft|looks|delivery]
	@test -n "$(P)" || (echo "Usage : make hf-render P=hf-demo [Q=delivery]" && exit 1)
	./scripts/hf render projects/$(P) --quality $(or $(Q),draft) --output output/$(P).mp4
