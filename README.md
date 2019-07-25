# Lookup activity stats by pid in Postgres

## Install

```sh
git clone https://github.com/tym-xqo/pid-lookup.git; cd pid-lookup
pipenv install
mv .env.example .env
ln -s ./pid_lookup.py /usr/local/bin/pidlkp
```

## Configure

Edit `.env` to suit your case

## Use

```sh
pidlkp <pid>
```

Output will look something like this contrived example

![pidlkp example](image/example.png)
