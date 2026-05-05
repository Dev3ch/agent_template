.PHONY: help new-module new-agent test lint fmt sync clean

# Conversión kebab-case → snake_case (para imports Python).
# Uso interno: $(call to_snake,my-agent) → my_agent
to_snake = $(subst -,_,$(1))

help: ## Mostrar ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

new-module: ## Crear módulo: make new-module name=marketing
	@if [ -z "$(name)" ]; then echo "Uso: make new-module name=<nombre>"; exit 1; fi
	@if [ -d "$(name)" ]; then echo "El módulo $(name) ya existe."; exit 1; fi
	@cp -r _template/module $(name)
	@MODULE_SNAKE=$$(echo "$(name)" | tr '-' '_'); \
	find $(name) -type f \( -name "*.md" -o -name "*.py" -o -name "*.toml" -o -name "*.sh" -o -name "*.json" -o -name "Dockerfile" -o -name ".env.example" -o -name ".dockerignore" \) \
		-exec sed -i "s/{{MODULE_NAME}}/$(name)/g; s/{{MODULE_SNAKE}}/$$MODULE_SNAKE/g" {} \;
	@# Hacer el módulo un paquete Python importable
	@touch $(name)/__init__.py $(name)/agents/__init__.py
	@chmod +x $(name)/service/build.sh $(name)/service/push.sh 2>/dev/null || true
	@echo "✔ Módulo '$(name)' creado en $(name)/"
	@echo "  Próximo paso: make new-agent module=$(name) name=<agente> type=<a|b|c>"

new-agent: ## Crear agente: make new-agent module=marketing name=google-ads type=a
	@if [ -z "$(module)" ] || [ -z "$(name)" ] || [ -z "$(type)" ]; then \
		echo "Uso: make new-agent module=<modulo> name=<agente> type=<a|b|c>"; \
		echo "  type=a: solo n8n (workflow). Sin código Python."; \
		echo "  type=b: híbrido (n8n + endpoint Python en service del módulo)."; \
		echo "  type=c: AgentLoop (n8n dispara, Python ejecuta loop con tools)."; \
		exit 1; \
	fi
	@if [ ! -d "$(module)" ]; then echo "El módulo $(module) no existe. Corré: make new-module name=$(module)"; exit 1; fi
	@AGENT_SNAKE=$$(echo "$(name)" | tr '-' '_'); \
	if [ -d "$(module)/agents/$$AGENT_SNAKE" ]; then \
		echo "El agente $(name) ya existe en $(module)/agents/$$AGENT_SNAKE/."; exit 1; \
	fi; \
	case "$(type)" in \
		a) src=_template/agent/type-a-n8n-only ;; \
		b) src=_template/agent/type-b-hybrid ;; \
		c) src=_template/agent/type-c-agentloop ;; \
		*) echo "type debe ser a, b o c"; exit 1 ;; \
	esac; \
	MODULE_SNAKE=$$(echo "$(module)" | tr '-' '_'); \
	if [ "$(type)" = "a" ]; then \
		mkdir -p "$(module)/agents/$$AGENT_SNAKE/prompts" "$(module)/workflows"; \
		cp "$$src/README.md" "$(module)/agents/$$AGENT_SNAKE/README.md"; \
		cp "$$src/prompts/system.md" "$(module)/agents/$$AGENT_SNAKE/prompts/system.md"; \
		cp "$$src/workflow.json" "$(module)/workflows/$(name).json"; \
		find "$(module)/agents/$$AGENT_SNAKE" "$(module)/workflows/$(name).json" -type f \
			-exec sed -i "s/{{AGENT_NAME}}/$(name)/g; s/{{AGENT_SNAKE}}/$$AGENT_SNAKE/g; s/{{MODULE_NAME}}/$(module)/g; s/{{MODULE_SNAKE}}/$$MODULE_SNAKE/g" {} \; ; \
	else \
		mkdir -p "$(module)/agents/$$AGENT_SNAKE" "$(module)/workflows"; \
		cp -r "$$src/." "$(module)/agents/$$AGENT_SNAKE/"; \
		mv "$(module)/agents/$$AGENT_SNAKE/workflow.json" "$(module)/workflows/$(name).json"; \
		find "$(module)/agents/$$AGENT_SNAKE" "$(module)/workflows/$(name).json" -type f \
			\( -name "*.py" -o -name "*.md" -o -name "*.json" \) \
			-exec sed -i "s/{{AGENT_NAME}}/$(name)/g; s/{{AGENT_SNAKE}}/$$AGENT_SNAKE/g; s/{{MODULE_NAME}}/$(module)/g; s/{{MODULE_SNAKE}}/$$MODULE_SNAKE/g" {} \; ; \
	fi; \
	echo "✔ Agente '$(name)' (tipo $(type)) creado en $(module)/agents/$$AGENT_SNAKE/"; \
	echo "  Workflow:  $(module)/workflows/$(name).json"; \
	if [ "$(type)" != "a" ]; then \
		echo ""; \
		echo "  ⚠ Falta registrarlo en $(module)/service/main.py — agregá:"; \
		echo "    from $$MODULE_SNAKE.agents.$$AGENT_SNAKE import core as $${AGENT_SNAKE}_agent"; \
		echo "    registry.register(\"$(name)\", $${AGENT_SNAKE}_agent.run)"; \
	fi

test: ## Correr tests (todos, sin integration)
	uv run pytest -m "not integration"

test-all: ## Correr todos los tests incluido integration
	uv run pytest

lint: ## Lint con ruff
	uv run ruff check .

fmt: ## Formatear con ruff
	uv run ruff format .

sync: ## Sincronizar dependencias del workspace
	uv sync

clean: ## Limpiar caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
