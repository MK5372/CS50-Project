import os
from flask import Flask, flash, redirect, render_template, request, session

db = SQL("sqlite://everything.db")
