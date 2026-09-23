"""Read saved briefs on open; a paid local generation always needs a button click."""
from datetime import datetime, timezone
import streamlit as st
from briefing.openai_client import DEFAULT_MODEL, BriefError
from briefing.service import daily_status, create_daily, edition_day, PARIS
from components.market_data import setting
from database.brief_store import BriefStore
from database.repository import StorageError


def show_report(report, current_day):
    stamp = datetime.fromisoformat(report["generated_at"].replace("Z", "+00:00")).astimezone(PARIS)
    if report["brief_date"] != current_day.isoformat():
        st.warning(f"Dernier brief disponible : {report['brief_date']}. Ce n'est pas l'édition du jour.")
    st.caption(f"Édition {report['brief_date']} · Généré à {stamp:%H:%M} Paris · Analyse IA sourcée")
    st.markdown(report["body"])
    with st.expander(f"Sources et traçabilité · {len(report['citations'])} références"):
        for i, citation in enumerate(report["citations"], 1):
            st.link_button(f"{i}. {citation['title']}", citation["url"])
        st.caption(f"Modèle : {report['model']} · Données arrêtées à {report['as_of']} · {report['prompt_version']}")


def render_brief(feeds):
    st.subheader("Brief TTF")
    st.caption("Les faits du jour · Lecture options · Catalyseurs à surveiller")
    if not st.session_state.get("db_user"):
        st.info("Connecte-toi pour lire le brief du matin, préparé à partir d'actualités vérifiées et des données du dashboard.")
        return
    store = BriefStore(st.session_state.db_client, st.session_state.db_user)
    now = datetime.now(timezone.utc)
    try:
        status = daily_status(store, now)
        report = status.get("report") if status["state"] == "success" else store.latest()
    except StorageError as exc:
        st.info(str(exc))
        st.page_link("views/admin.py", label="Configurer le brief →")
        return
    pending = st.session_state.get("brief_unsaved")
    if pending:
        st.warning("Un résultat reste à enregistrer. Réessayer la sauvegarde ne fait pas de nouvel appel OpenAI.")
        if st.button("Réessayer la sauvegarde du brief"):
            try:
                store.save(pending)
            except StorageError as exc:
                st.error(str(exc))
            else:
                st.session_state.pop("brief_unsaved", None)
                st.rerun()
        if pending["status"] == "success":
            st.caption("Aperçu non encore archivé")
            show_report(pending, edition_day(now))
        return
    if report:
        show_report(report, status["day"])
    else:
        st.info("Aucun brief archivé. La préparation quotidienne est prévue à 6 h, heure de Paris, via GitHub Actions.")
    if status["state"] == "running":
        st.caption("Génération déjà en cours. Le résultat apparaîtra après actualisation.")
        return
    if status["state"] in {"failed", "interrupted"}:
        st.warning(status.get("report", {}).get("error_message", "La précédente génération n'a pas abouti.") if status.get("report") else "La précédente génération a été interrompue.")
    if status["state"] != "success" and now.astimezone(PARIS).hour >= 6:
        configured = bool(setting("OPENAI_API_KEY"))
        retry = status["state"] in {"failed", "interrupted"}
        if configured:
            label = "Réessayer le brief (nouvel appel API)" if retry else "Générer le brief du jour"
            if st.button(label, disabled=status.get("attempt", 0) >= 2, type="primary"):
                try:
                    with st.spinner("Recherche des actualités et rédaction du brief…"):
                        result = create_daily(store, feeds, setting("OPENAI_API_KEY"),
                                              setting("OPENAI_BRIEF_MODEL") or DEFAULT_MODEL, retry=retry)
                    if result["state"] == "unsaved":
                        st.session_state["brief_unsaved"] = result["report"]
                    st.rerun()
                except (BriefError, StorageError) as exc:
                    st.error(str(exc))
            st.caption("Un brief archivé par jour ; au maximum une relance manuelle après un échec. Appels facturés par l'API OpenAI.")
        else:
            st.caption("La clé OpenAI dans GitHub suffit pour le brief planifié. Ajoute-la aussi localement pour pouvoir lancer un brief ici.")
            st.page_link("views/admin.py", label="Voir la configuration →")
    elif now.astimezone(PARIS).hour < 6:
        st.caption("La prochaine édition est prévue à 6 h, heure de Paris.")
