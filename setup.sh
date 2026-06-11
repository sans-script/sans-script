#!/bin/bash

# Update the system
sudo apt update && sudo apt upgrade -y

# Install Zsh and useful tools
sudo apt install zsh git wget neofetch unzip -y

# Install Oh My Zsh
export RUNZSH=no
export CHSH=no
sh -c "$(wget https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh -O -)"

[ -f "$HOME/.zshrc" ] || cp "$HOME/.oh-my-zsh/templates/zshrc.zsh-template" "$HOME/.zshrc"

# Install Spaceship Prompt
git clone https://github.com/spaceship-prompt/spaceship-prompt.git "$HOME/.oh-my-zsh/custom/themes/spaceship-prompt" --depth=1
ln -sf "$HOME/.oh-my-zsh/custom/themes/spaceship-prompt/spaceship.zsh-theme" "$HOME/.oh-my-zsh/custom/themes/spaceship.zsh-theme"

# Install Nerd Font (FiraCode)
mkdir -p ~/.local/share/fonts
cd ~/.local/share/fonts
wget https://github.com/ryanoasis/nerd-fonts/releases/latest/download/FiraCode.zip
unzip -o FiraCode.zip
fc-cache -fv
cd ~

# Update ZSH_THEME line only
sed -i 's/^ZSH_THEME=.*/ZSH_THEME="spaceship"/' ~/.zshrc

# Insert Spaceship config block if not present
CONFIG_BLOCK=$(cat <<'EOF'

# BEGIN SPACESHIP CONFIG
SPACESHIP_PROMPT_ORDER=(
  user
  dir
  host
  git
  exec_time
  line_sep
  jobs
  exit_code
  char
)
SPACESHIP_USER_SHOW=always
SPACESHIP_USER_SUFFIX=" "
SPACESHIP_PROMPT_ADD_NEWLINE=false
SPACESHIP_CHAR_SYMBOL="→ "
SPACESHIP_CHAR_SUFFIX="$ "
# END SPACESHIP CONFIG
EOF
)

if ! grep -q '# BEGIN SPACESHIP CONFIG' ~/.zshrc; then
  echo -e "$CONFIG_BLOCK" >> ~/.zshrc
fi

# Set zsh as the default shell
chsh -s "$(which zsh)"

# Start zsh
exec zsh
