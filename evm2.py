import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# Constants
ADMIN_PASSWORD = "SMBAvoting1234"
SPECIAL_VOTE_PASSWORD = "SMBAvoting4321"
DATA_DIR = "data"
CANDIDATES_FILE = os.path.join(DATA_DIR, "candidates.json")
VOTES_FILE = os.path.join(DATA_DIR, "votes.json")
VOTERS_FILE = os.path.join(DATA_DIR, "voters.json")
CANDIDATE_SYMBOLS_FILE = os.path.join(DATA_DIR, "candidate_symbols.json")


# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Initialize data files if they don't exist
def initialize_data_files():
    if not os.path.exists(CANDIDATES_FILE):
        initial_candidates = {
            "Chief Minister": ["Arya Naik (Yuva Shakti)", "Virendrasinh Chavan (True Companions)"],
            "Deputy Chief Minister": ["Saee Jitkar(Justice League)", "Ishita Kamble(True Companions)", "Saee Thakur (Yuva Shakti)"],
            "Home Minister (Boys)": ["Aadish Charate (Swastik Sena)", "Advit Katyare (True Companions)", "Aaditya Bandekar (Yuva Shakti)"],
            "Home Minister (Girls)": ["Sai Raut (True Companions)", "Sanvi Bagal(Justice League)", "Arushi Patil"],
            "Cultural Minister (Boys)": ["Tanishk Khandekar (True Companions)", "Sharvil Rege (Yuva  Shakti)"],
            "Cultural Minister (Girls)": ["Isha Deshpande (Justice League)", "Ayushi Dalvi (True Companions)", "Ritika Magdum (Yuva Shakti)"],
            "Sports Minister (Boys)": ["Noman Peerjade (True Companions)", "Indranil Velhal (Yuva Shakti)"],
            "Sports Minister (Girls)": ["Shourya Takkalki (Justice League)", "Angha Borate (True Companions)", "Aryaa Patil (Yuva Shakti)"],
            "Health and Discipline Minister (Boys)": ["Ali Shaikhlal (True Companions)", "Jinay Mehta (Yuva Shakti)"],
            "Health and Discipline Minister (Girls)": ["Samruddhi Patil (Justice League)", "Maitrayi Bhosle (True Companions)", "Avani Chougule (Yuva Shakti)"]
        }
        save_json(CANDIDATES_FILE, initial_candidates)
    
    if not os.path.exists(VOTES_FILE):
        save_json(VOTES_FILE, {})
    
    if not os.path.exists(VOTERS_FILE):
        save_json(VOTERS_FILE, {})

def load_json(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def load_candidates():
    return load_json(CANDIDATES_FILE)

def save_candidates(candidates):
    save_json(CANDIDATES_FILE, candidates)

def load_votes():
    return load_json(VOTES_FILE)

def save_votes(votes):
    save_json(VOTES_FILE, votes)

def load_voters():
    return load_json(VOTERS_FILE)

def save_voters(voters):
    save_json(VOTERS_FILE, voters)

def load_candidate_symbols():
    return load_json(CANDIDATE_SYMBOLS_FILE)

def save_candidate_symbols(symbols):
    save_json(CANDIDATE_SYMBOLS_FILE, symbols)


def has_voter_voted_for_position(voter_id, position):
    voters = load_voters()
    return voter_id in voters and position in voters[voter_id]

def record_voter_vote(voter_id, position):
    voters = load_voters()
    if voter_id not in voters:
        voters[voter_id] = []
    voters[voter_id].append(position)
    save_voters(voters)

def view_voters():
    st.subheader("📋 List of Voters")
    
    voters = load_voters()
    
    if not voters:
        st.info("No voters have cast their votes yet.")
        return
    
    # Convert voters dict into a DataFrame for easy display
    voter_data = []
    for voter_id, positions in voters.items():
        voter_data.append({
            "Voter ID": voter_id,
            "Positions Voted": ", ".join(positions) if positions else "None"
        })
    
    df = pd.DataFrame(voter_data)
    st.dataframe(df, use_container_width=True)


def cast_vote(position, candidate, voter_id, vote_weight=1):
    votes = load_votes()
    vote_key = f"{position}_{candidate}"
    
    if vote_key not in votes:
        votes[vote_key] = 0
    
    votes[vote_key] += vote_weight
    save_votes(votes)
    record_voter_vote(voter_id, position)

def get_results():
    votes = load_votes()
    candidates = load_candidates()
    results = {}
    
    for position in candidates:
        results[position] = {}
        for candidate in candidates[position]:
            vote_key = f"{position}_{candidate}"
            results[position][candidate] = votes.get(vote_key, 0)
    
    return results

def voting_interface():
    st.header("🗳️ Electronic Voting Machine")
    st.subheader("SMBA School Elections")
    
    # Initialize session state for voting completion
    if 'voting_completed' not in st.session_state:
        st.session_state.voting_completed = False
    
    # Check if voting was just completed
    if st.session_state.voting_completed:
        st.success("🎉 Thank you for voting!")
        st.info("Your votes have been recorded successfully.")
        st.markdown("---")
        if st.button("Start New Voting Session", type="primary"):
            st.session_state.voting_completed = False
            st.rerun()
        return
    
    # Voter ID input
    voter_id = st.text_input("Enter your Voter ID:", placeholder="e.g., STU001, TCH001, etc.")
    
    if not voter_id:
        st.warning("Please enter your Voter ID to proceed with voting.")
        return
    
    # Check for special vote type
    vote_weight = 1
    voter_type = "Student"
    
    if st.checkbox("I am a Teacher/Principal (requires password)"):
        special_password = st.text_input("Enter special voting password:", type="password")
        if special_password == SPECIAL_VOTE_PASSWORD:
            voter_type_selection = st.radio("Select your role:", ["Teacher", "Principal"])
            if voter_type_selection == "Teacher":
                vote_weight = 5
                voter_type = "Teacher"
            elif voter_type_selection == "Principal":
                vote_weight = 10
                voter_type = "Principal"
            st.success(f"Special voting rights activated for {voter_type} (Weight: {vote_weight})")
        elif special_password:
            st.error("Invalid special voting password!")
            return
    
    st.info(f"Voting as: {voter_type} (Vote Weight: {vote_weight})")
    
    candidates = load_candidates()
    
    # Display voting interface for each position
    st.subheader("Select Candidates for Each Position")
    
    # Count how many positions this voter has already voted for
    voted_positions = 0
    total_positions_with_candidates = 0
    
    for position in candidates:
        if candidates[position]:  # Only count positions that have candidates
            total_positions_with_candidates += 1
            if has_voter_voted_for_position(voter_id, position):
                voted_positions += 1
    
    # Show voting progress
    if total_positions_with_candidates > 0:
        st.progress(voted_positions / total_positions_with_candidates)
        st.caption(f"Progress: {voted_positions}/{total_positions_with_candidates} positions voted")
    
    votes_cast = 0
    
    for position in candidates:
        if not candidates[position]:
            st.warning(f"No candidates available for {position}")
            continue
            
        st.markdown(f"### {position}")
        
        # Check if voter has already voted for this position
        if has_voter_voted_for_position(voter_id, position):
            st.success(f"✅ You have already voted for {position}")
            continue
        
        # Create voting interface for this position
        selected_candidate = st.radio(
            f"Choose a candidate for {position}:",
            candidates[position] + ["Skip this position"],
            key=f"vote_{position}"
        )
        symbols = load_candidate_symbols()
        if position in candidates:   # ✅ ensures candidates[position] exists
            for cand in candidates[position]:
                if cand in symbols and os.path.exists(symbols[cand]):
                    st.image(symbols[cand], width=100, caption=cand)

        if selected_candidate != "Skip this position":
            if st.button(f"Cast Vote for {position}", key=f"cast_{position}"):
                cast_vote(position, selected_candidate, voter_id, vote_weight)
                st.success(f"Vote cast for {selected_candidate} in {position}!")
                votes_cast += 1
                st.rerun()
    
    if votes_cast > 0:
        st.balloons()
    
    # Complete Voting Button (always show at the bottom)
    st.markdown("---")
    st.subheader("Finish Voting")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write("Click the button below when you're done voting to return to the main menu.")
    with col2:
        if st.button("🏁 Complete Voting", type="primary", key="complete_voting"):
            st.session_state.voting_completed = True
            st.rerun()

def admin_panel():
    st.header("🔧 Admin Panel")
    
    # Admin authentication
    admin_password = st.text_input("Enter Admin Password:", type="password")
    
    if admin_password != ADMIN_PASSWORD:
        if admin_password:
            st.error("Invalid admin password!")
        else:
            st.warning("Please enter the admin password to access the admin panel.")
        return
    
    st.success("Admin access granted!")
    
    # Admin menu
    admin_option = st.selectbox("Select Admin Function:", [
        "Manage Candidates",
        "Add Candidate Symbols",
        "View Results",
        "View Voters",
        "Reset Election Data",
        "Export Results"
    ])
    
    if admin_option == "Manage Candidates":
        manage_candidates()
    elif admin_option == "View Results":
        view_results()
    elif admin_option == "Reset Election Data":
        reset_election_data()
    elif admin_option == "Export Results":
        export_results()
    elif admin_option == "View Voters":
        view_voters()
    elif admin_option == "Add Candidate Symbol":
        manage_candidate_symbols()


def manage_candidates():
    st.subheader("Candidate Management")
    
    candidates = load_candidates()
    
    # Select position to manage
    position = st.selectbox("Select Position to Manage:", list(candidates.keys()))
    
    st.markdown(f"### Current Candidates for {position}")
    if candidates[position]:
        for i, candidate in enumerate(candidates[position]):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"{i+1}. {candidate}")
            with col2:
                if st.button("Remove", key=f"remove_{position}_{i}"):
                    candidates[position].remove(candidate)
                    save_candidates(candidates)
                    st.success(f"Removed {candidate} from {position}")
                    st.rerun()
    else:
        st.info("No candidates added for this position yet.")
    
    # Add new candidate
    st.markdown("### Add New Candidate")
    new_candidate = st.text_input(f"Enter candidate name for {position}:")
    if st.button("Add Candidate"):
        if new_candidate and new_candidate not in candidates[position]:
            candidates[position].append(new_candidate)
            save_candidates(candidates)
            st.success(f"Added {new_candidate} to {position}")
            st.rerun()
        elif new_candidate in candidates[position]:
            st.error("Candidate already exists for this position!")
        else:
            st.error("Please enter a candidate name!")
    
    # Rename position
    st.markdown("### Rename Position")
    new_position_name = st.text_input(f"Enter new name for '{position}':")
    if st.button("Rename Position"):
        if new_position_name and new_position_name != position:
            candidates[new_position_name] = candidates.pop(position)
            save_candidates(candidates)
            st.success(f"Renamed '{position}' to '{new_position_name}'")
            st.rerun()


def manage_candidate_symbols():
    st.subheader("Add Candidate Symbols")

    candidates = load_candidates()   # ✅ load from your JSON

    if not candidates:
        st.info("No candidates found. Please add candidates first.")
        return

    for position, cand_list in candidates.items():
        st.write(f"### {position}")   # show the position name
        for cand in cand_list:
            st.write(f"Candidate: {cand}")
            uploaded_file = st.file_uploader(
                f"Upload symbol for {cand}",
                type=["png", "jpg", "jpeg"],
                key=f"symbol_{position}_{cand}"
            )
            if uploaded_file is not None:
                # Save to symbols folder
                save_path = os.path.join("symbols", f"{cand}.png")
                os.makedirs("symbols", exist_ok=True)
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"Symbol for {cand} uploaded successfully!")
                # Update JSON mapping
                symbols = load_candidate_symbols()
                symbols[cand] = save_path
                save_candidate_symbols(symbols)




def view_results():
    st.subheader("Election Results")
    
    results = get_results()
    
    for position in results:
        st.markdown(f"### {position}")
        if results[position]:
            # Create DataFrame for better display
            position_results = []
            for candidate, votes in results[position].items():
                position_results.append({"Candidate": candidate, "Votes": votes})
            
            if position_results:
                df = pd.DataFrame(position_results).sort_values("Votes", ascending=False)
                st.dataframe(df, use_container_width=True)
                
                # Show winner
                if df["Votes"].max() > 0:
                    winner = df.iloc[0]
                    st.success(f"🏆 Leading: {winner['Candidate']} with {winner['Votes']} votes")
                else:
                    st.info("No votes cast yet for this position")
            else:
                st.info("No candidates for this position")
        else:
            st.info("No candidates available for this position")

def reset_election_data():
    st.subheader("Reset Election Data")
    st.warning("⚠️ This action will permanently delete all voting data!")
    
    if st.checkbox("I understand this action cannot be undone"):
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Reset Votes Only", type="secondary"):
                save_votes({})
                save_voters({})
                st.success("All votes have been reset!")
                st.rerun()
        
        with col2:
            if st.button("Reset Everything", type="primary"):
                save_votes({})
                save_voters({})
                initial_candidates = {f"Position {i}": [] for i in range(1, 11)}
                save_candidates(initial_candidates)
                st.success("All election data has been reset!")
                st.rerun()

def export_results():
    st.subheader("Export Results")
    
    results = get_results()
    
    # Create comprehensive results report
    report_data = []
    for position in results:
        for candidate, votes in results[position].items():
            report_data.append({
                "Position": position,
                "Candidate": candidate,
                "Votes": votes
            })
    
    if report_data:
        df = pd.DataFrame(report_data)
        
        # Display summary
        st.markdown("### Results Summary")
        st.dataframe(df, use_container_width=True)
        
        # Convert to CSV for download
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download Results as CSV",
            data=csv,
            file_name=f"election_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        # Show total votes cast
        total_votes = df["Votes"].sum()
        st.metric("Total Votes Cast", total_votes)
    else:
        st.info("No voting data available to export.")

def main():
    # Initialize data files
    initialize_data_files()
    
    # Page configuration
    st.set_page_config(
        page_title="SMBA Electronic Voting Machine",
        page_icon="🗳️",
        layout="wide"
    )
    
    # Main title
    st.title("🏫 SMBA School Electronic Voting Machine")
    
    # Navigation
    tab1, tab2 = st.tabs(["🗳️ Vote", "🔧 Admin Panel"])
    
    with tab1:
        voting_interface()
    
    with tab2:
        admin_panel()
    
    # Footer
    st.markdown("---")
    st.markdown("*SMBA School Elections - Portable Electronic Voting System*")

if __name__ == "__main__":
    main()


def display_candidate_symbol(candidate_name):
    symbols = load_candidate_symbols()
    if candidate_name in symbols and os.path.exists(symbols[candidate_name]):
        st.image(symbols[candidate_name], width=80, caption=candidate_name)












