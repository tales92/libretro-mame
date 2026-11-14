#!/usr/bin/env python3
"""Generate reader-friendly Brazilian Portuguese notes for MAME Libretro releases."""
from __future__ import annotations

import argparse
import re
import subprocess
from collections import defaultdict
from pathlib import Path

BT = chr(96)


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], check=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    return result.stdout.strip()


def clean_name(value: str) -> str:
    value = re.sub(r"\s+\[[^\]]+\]", "", value)
    value = re.sub(r"\s+\(#\d+\)", "", value)
    return re.sub(r"\s+", " ", value).strip(" -:;.")


def machine_label(paths: list[str]) -> str:
    for path in paths:
        match = re.search(r"src/mame/([^/]+)/([^/]+)\.(?:cpp|h)$", path)
        if match:
            family = match.group(1).replace("_", " ").upper()
            if family in {"MISC", "SKELETON"}:
                family = match.group(2).replace("_", " ").title()
            return family
    for path in paths:
        match = re.search(r"src/devices/(?:machine|bus|cpu)/([^/]+)/", path)
        if match:
            return "hardware " + match.group(1).replace("_", " ").upper()
    return ""


def describe(subject: str, paths: list[str]) -> tuple[str, str]:
    text = re.sub(r"\s+", " ", subject).strip()
    low = text.lower()
    path_text = " ".join(paths).lower()

    if "new working clone" in low or "new working set" in low:
        item = re.sub(r"^.*?new working clones?\s*-+\s*", "", text, flags=re.I)
        item = clean_name(item)
        return "new", (
            f"**{item}** — nova versão/conjunto reconhecido pelo MAME como funcional. "
            "A execução continua dependendo das ROMs correspondentes."
        )

    if "new clone" in low and ("not working" in low or "marked not working" in low):
        item = re.sub(r"^.*?new clones? marked not working\s*-+\s*", "", text, flags=re.I)
        item = clean_name(item)
        return "new", (
            f"**{item}** — novas variantes foram cadastradas, mas continuam marcadas como não funcionais. "
            "Elas passam a ser documentadas pelo MAME, mas não devem ser anunciadas como jogáveis."
        )

    promoted = (
        "working" in low
        and ("promot" in low or "mark " in low or "marked " in low or "machine_not_working" in low)
        and "not working" not in low
    )
    if promoted:
        item = clean_name(re.sub(r"^[^:]+:\\s*", "", text))
        return "new", (
            f"**{item}** — máquina ou versão promovida para o estado funcional no MAME. "
            "Isso indica que ela deixou de ser marcada como não funcional; ainda é recomendável testar o funcionamento no core."
        )

    if "star attack" in low and "galaxian" in path_text:
        return "new", (
            "**Star Attack (Hiraoka New York)** — novo jogo de arcade incluído no catálogo, "
            "com a implementação inicial necessária para emular sua placa."
        )

    if "radio shack color graphics printer" in low or "cgp-220" in low:
        return "new", (
            "**Radio Shack Color Graphics Printer CGP-220** — adicionado suporte a essa impressora "
            "de computador antigo, ampliando a preservação de periféricos históricos."
        )

    if "vgame" in low and any(word in low for word in ("research", "cpu", "encryption")):
        return "emulation", (
            "**Hardware VGame** — avanço na investigação do processador e do sistema de proteção da placa. "
            "É pesquisa e documentação; não significa, por si só, que um novo jogo já esteja funcional."
        )

    if "lzma" in low and any(word in low for word in ("zip", "decompress", "method 14")):
        return "fixes", (
            "**Arquivos ZIP com compressão LZMA** — corrigida a verificação de erros durante a descompactação. "
            "Isso torna a leitura desse tipo de arquivo mais confiável."
        )

    if "igs027a" in low and any(word in low for word in ("irq", "interrupt")):
        return "fixes", (
            "**Extra Draw e Xingyun Xiaochou** — ajustado o tratamento de interrupções do hardware IGS027A, "
            "permitindo que esses jogos avancem até a inicialização. Isso ainda não confirma funcionamento completo."
        )

    if "xyxcxysj" in low and any(word in low for word in ("dip", "test mode", "input")):
        return "fixes", (
            "**Xingyun Xiaochou (xyxcxysj)** — preenchidas as opções de configuração exibidas no menu de teste, "
            "melhorando a identificação dos controles e ajustes da máquina."
        )

    if "witch game" in low and any(word in low for word in ("dip", "coinage", "initial settings")):
        return "fixes", (
            "**Série Witch Game** — corrigidas configurações iniciais de créditos e opções da máquina, "
            "incluindo ajustes acessíveis pelo menu de serviço."
        )

    if ("newxpang" in low or "new cross pang" in low) and ("speed" in low or "speedup" in low):
        return "fixes", "**New Cross Pang** — ajustado o tratamento de velocidade da segunda versão do jogo."

    if "renamed" in low or "rename" in low:
        if "src/mame/" in path_text:
            return "other", (
                "**Identificação de jogos e versões** — nomes de conjuntos foram reorganizados para distinguir "
                "melhor as variantes cadastradas. É uma atualização do catálogo, não um jogo novo."
            )

    if any(word in low for word in (" added ", "add support", "added support", "new machine", "new system")) and "src/mame/" in path_text:
        target = machine_label(paths) or clean_name(text)
        return "new", (
            f"**{target}** — atualização do suporte a uma máquina, jogo ou versão no catálogo do MAME. "
            "O commit vinculado traz os detalhes específicos."
        )

    if any(word in low for word in ("fix", "fixed", "correct", "corrected", "bug")):
        if "hash/" in path_text:
            return "fixes", (
                "**Biblioteca de jogos e mídias** — corrigidas informações usadas para identificar arquivos e versões, "
                "ajudando o MAME a reconhecer corretamente os materiais preservados."
            )
        target = machine_label(paths)
        if target:
            return "fixes", f"**{target}** — correção na emulação ou no comportamento dessa família de máquinas."
        return "fixes", (
            "**Correção de funcionamento** — resolvido um problema interno identificado nesta atualização. "
            "O commit vinculado mostra o componente afetado."
        )

    if "src/devices/" in path_text or "src/emu/" in path_text:
        target = machine_label(paths)
        detail = f"na emulação de {target}" if target else "no funcionamento interno do emulador"
        return "emulation", (
            f"**Melhoria de emulação** — ajuste {detail}, reforçando a precisão ou a compatibilidade. "
            "O link do commit traz o contexto específico."
        )

    if "docs/" in path_text or "documentation" in low or low.startswith("docs:"):
        return "other", "**Documentação** — textos e referências do projeto foram atualizados."

    if "src/mame/" in path_text:
        target = machine_label(paths)
        if target:
            return "emulation", f"**{target}** — melhoria interna relacionada à emulação dessa família de máquinas."

    return "other", (
        "**Manutenção interna** — ajuste no código ou nos dados do MAME. "
        "O título original não indica uma mudança diretamente visível ao jogador."
    )


def collect(previous_sha: str, upstream_sha: str) -> list[dict[str, str]]:
    shas = git("rev-list", "--reverse", "--no-merges", f"{previous_sha}..{upstream_sha}").split()
    result = []
    for sha in shas:
        subject = git("show", "-s", "--format=%s", sha)
        paths = git("diff-tree", "--no-commit-id", "--name-only", "-r", sha).splitlines()
        section, description = describe(subject, paths)
        result.append({
            "sha": sha, "subject": subject, "section": section,
            "description": description,
            "url": f"https://github.com/mamedev/mame/commit/{sha}",
        })
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--previous-upstream-sha", required=True)
    parser.add_argument("--upstream-sha", required=True)
    parser.add_argument("--integration-commit", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--asset-dir", default="release-assets")
    parser.add_argument("--output", default="release-notes.md")
    args = parser.parse_args()

    for sha in (args.previous_upstream_sha, args.upstream_sha, args.integration_commit):
        git("cat-file", "-e", f"{sha}^{{commit}}")

    packages = sorted(Path(args.asset_dir).glob("*.zip"))
    if len(packages) != 2:
        raise SystemExit(f"Expected exactly two platform ZIP packages; found {len(packages)}.")

    commits = collect(args.previous_upstream_sha, args.upstream_sha)
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for item in commits:
        grouped[item["section"]].append(item)

    lines = [
        f"# MAME Libretro Current — {args.version}",
        "",
        "Esta publicação reúne uma atualização do MAME oficial, adaptada para funcionar como core do RetroArch.",
        "O resumo destaca o impacto em jogos, máquinas e recursos, sem esconder os links para os registros originais.",
        "",
        "## Downloads",
        "",
    ]
    for package in packages:
        name = package.name.lower()
        if "windows" in name:
            lines.append(f"- **Windows 64 bits:** {BT}{package.name}{BT} — core {BT}mame_libretro.dll{BT}.")
        elif "linux" in name:
            lines.append(f"- **Linux 64 bits:** {BT}{package.name}{BT} — core {BT}mame_libretro.so{BT}.")
        else:
            lines.append(f"- {BT}{package.name}{BT}.")
    lines += [
        "",
        f"Cada pacote inclui informações da compilação e o checksum SHA-256 para conferir a integridade. Foram incorporados **{len(commits)} commits do MAME oficial** nesta atualização.",
        "",
        "## O que mudou nesta atualização",
        "",
    ]

    for key, title in [
        ("new", "Novas máquinas, jogos e versões"),
        ("fixes", "Jogos e recursos que receberam correções"),
        ("emulation", "Melhorias na emulação e na compatibilidade"),
        ("other", "Outras mudanças e manutenção"),
    ]:
        entries = grouped.get(key, [])
        lines += [f"### {title}", ""]
        if not entries:
            lines += ["Nenhuma alteração identificada nesta categoria nesta atualização.", ""]
            continue
        for item in entries:
            lines.append(f"- {item['description']} ([ver alteração]({item['url']})).")
        lines.append("")

    lines += [
        "## Origem e validação",
        "",
        "- **Base histórica do fork:** MAME 0.289.",
        "- **Projeto de origem:** [mamedev/mame](https://github.com/mamedev/mame), branch " + BT + "master" + BT + ".",
        f"- **Commit upstream anterior:** [{args.previous_upstream_sha[:12]}](https://github.com/mamedev/mame/commit/{args.previous_upstream_sha}).",
        f"- **Novo commit upstream integrado:** [{args.upstream_sha[:12]}](https://github.com/mamedev/mame/commit/{args.upstream_sha}).",
        f"- **Commit de integração:** [{args.integration_commit[:12]}](https://github.com/{args.repository}/commit/{args.integration_commit}).",
        "- As builds Windows e Linux passaram pela compilação e pela verificação do formato e da arquitetura dos binários.",
        "- O GitHub Actions não testa jogos dentro do RetroArch; a validação prática depende de testes no emulador.",
        "",
        "<details>",
        "<summary>Ver títulos originais dos commits (referência técnica)</summary>",
        "",
    ]
    for item in commits:
        lines.append(f"- {item['subject']} ([{item['sha'][:12]}]({item['url']})).")
    lines += ["", "</details>", ""]
    Path(args.output).write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
