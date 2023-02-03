#!/usr/bin/env python
# coding: utf-8

# In[6]:


#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import pandas as pd
import numpy as np
from shroomdk import ShroomDK
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.ticker as ticker
import numpy as np
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
sdk = ShroomDK("679043b4-298f-4b7f-9394-54d64db46007")
st.set_page_config(page_title="Near Weekly Report", layout="wide",initial_sidebar_state="collapsed")


# In[2]:


import time
my_bar = st.progress(0)

for percent_complete in range(100):
    time.sleep(0.1)
    my_bar.progress(percent_complete + 1)


# In[7]:


st.title('Near Weekly Report')
st.write('')
st.markdown('**Near Protocol** Near Protocol is a decentralized application (DApp) platform that focuses on usability among developers and users. As a competitor of Ethereum, NearProtocol is also smart-contract capable and a proof-of-stake (PoS) blockchain. It uses sharding technology to achieve scalability, a core aspect discussed later. The native token, NEAR, is used for transaction fees and storage on the Near crypto platform. Tokens can also be used for staking by NEAR tokenholders who wish to become transaction validators and help achieve network consensus.')
st.markdown('Near was built by the NeaCollective and conceptualized as a community-run cloud computing platform designed to host decentralized applications. It was also built to be both developer and user-friendly, hence having features such as account names that are human-readable (instead of cryptographic wallet addresses).')
st.markdown('**How does Near Protocol work?** Decentralized applications have boomed in the crypto community, with DApps that run the gamut from games to financial services. However, it has also become apparent that scalability remains a problem in most blockchains.')
st.markdown('The issue of scalability is common among blockchains, especially among older ones such as Bitcoin and Ethereum. The challenges are mainly brought about by blockchains difficulty in handling large numbers of transactions at fast speeds and manageable costs.')
st.markdown('The intention of this analysis is to take a look at the following main aspects of **Near Protocol**:')
st.markdown('1. Active users')
st.markdown('2. New users')
st.markdown('3. Active contracts')
st.markdown('4. New contracts')
st.markdown('5. Transactions')
st.markdown('6. Fees')
st.markdown('7. Gas used')
st.markdown('8. Proposed metric to add')
st.write('')

st.subheader('1. Near users')
st.markdown('**Methods:**')
st.write('In this analysis we will focus on Near user activity. More specifically, we will analyze the following data:')
st.markdown('● Hourly active users.')
st.markdown('● Daily active users.')
st.markdown('● Hourly new users.')
st.markdown('● Daily new users.')
st.write('')

sql="""
with 
t1 as (
SELECT
trunc(x.block_timestamp,'hour') as date,
count(distinct x.tx_hash) as transactions,
count(distinct x.tx_signer) as active_users,
transactions/active_users as avg_tx_per_user,
sum(transaction_fee/pow(10,24)) as fees,
avg(transaction_fee/pow(10,24)) as avg_tx_fee
  from near.core.fact_transactions x
  where x.block_timestamp>=current_date-INTERVAL '1 WEEK'
  group by 1
  ),
  t2 as (
  select
distinct tx_signer as user,
min (block_timestamp) as first_date
  from near.core.fact_transactions
  group by 1
  ),
  t3 as (
  select
  trunc(first_date,'hour') as date,
count(distinct user) as new_users
  from t2 where first_date>=current_date-INTERVAL '1 WEEK'
  group by 1
  )
  SELECT
  t1.date,active_users,new_users
  from t1,t3 where t1.date=t3.date
order by 1 asc 

"""

sql2="""
with 
t1 as (
SELECT
trunc(x.block_timestamp,'day') as date,
count(distinct x.tx_hash) as transactions,
count(distinct x.tx_signer) as active_users,
transactions/active_users as avg_tx_per_user,
sum(transaction_fee/pow(10,24)) as fees,
avg(transaction_fee/pow(10,24)) as avg_tx_fee
  from near.core.fact_transactions x
  where x.block_timestamp>=current_date-INTERVAL '1 WEEK'
  group by 1
  ),
  t2 as (
  select
distinct tx_signer as user,
min (block_timestamp) as first_date
  from near.core.fact_transactions
  group by 1
  ),
  t3 as (
  select
  trunc(first_date,'day') as date,
count(distinct user) as new_users
  from t2 where first_date>=current_date-INTERVAL '1 WEEK'
  group by 1
  )
  SELECT
  t1.date,active_users,new_users
  from t1,t3 where t1.date=t3.date
order by 1 asc 

"""

st.experimental_memo(ttl=50000)
def memory(code):
    data=sdk.query(code)
    return data

results = memory(sql)
df = pd.DataFrame(results.records)
df.info()

results2 = memory(sql2)
df2 = pd.DataFrame(results2.records)
df2.info()

with st.expander("Check hourly activity"):
    st.altair_chart(alt.Chart(df)
        .mark_line()
        .encode(x='date:N', y='active_users:Q')
        .properties(width=1200,title='Hourly active users'))
    
    st.altair_chart(alt.Chart(df)
        .mark_line()
        .encode(x='date:N', y='new_users:Q')
        .properties(width=1200,title='Hourly new users'))

with st.expander("Check daily activity"):
    st.altair_chart(alt.Chart(df2)
        .mark_line()
        .encode(x='date:N', y='active_users:Q')
        .properties(width=1200,title='Daily active users'))
    
    st.altair_chart(alt.Chart(df2)
        .mark_line()
        .encode(x='date:N', y='new_users:Q')
        .properties(width=1200,title='Daily new users'))
    
    
    
    
    
st.subheader('2. Near contracts')
st.markdown('**Methods:**')
st.write('In this analysis we will focus on Near development. More specifically, we will analyze the following data:')
st.markdown('● Hourly active contracts.')
st.markdown('● Daily active contracts.')
st.markdown('● Hourly new contracts.')
st.markdown('● Daily new contracts.')
st.write('')

sql="""
select
trunc(x.block_timestamp,'hour') as date,
  count(distinct receiver_id) as active_contracts
from near.core.fact_actions_events x  
join near.core.fact_receipts y on x.tx_hash=y.tx_hash
where action_name <> 'DeployContract'
and date >= CURRENT_DATE - INTERVAL '1 WEEK'
group by 1
order by 1 asc 

"""

sql2="""
select
trunc(x.block_timestamp,'day') as date,
  count(distinct receiver_id) as active_contracts
from near.core.fact_actions_events x  
join near.core.fact_receipts y on x.tx_hash=y.tx_hash
where action_name <> 'DeployContract'
and date >= CURRENT_DATE - INTERVAL '1 WEEK'
group by 1
order by 1 asc
"""

sql3="""
SELECT
trunc(first_date,'hour') as date,
count(distinct receiver_id ) as new_contracts,
  sum(new_contracts) over (order by date) as cum_new_contracts
from (select
  receiver_id,
  min(x.block_timestamp) as first_date
from near.core.fact_actions_events x  
join near.core.fact_receipts y on x.tx_hash=y.tx_hash
where action_name = 'DeployContract'
  group by 1) where first_date >= CURRENT_DATE - INTERVAL '1 WEEK'
group by 1
order by 1 asc 

"""

sql4="""
SELECT
trunc(first_date,'day') as date,
count(distinct receiver_id ) as new_contracts,
  sum(new_contracts) over (order by date) as cum_new_contracts
from (select
  receiver_id,
  min(x.block_timestamp) as first_date
from near.core.fact_actions_events x  
join near.core.fact_receipts y on x.tx_hash=y.tx_hash
where action_name = 'DeployContract'
  group by 1) where first_date >= CURRENT_DATE - INTERVAL '1 WEEK'
group by 1
order by 1 asc 
"""

st.experimental_memo(ttl=50000)
def memory(code):
    data=sdk.query(code)
    return data

results = memory(sql)
df = pd.DataFrame(results.records)
df.info()

results2 = memory(sql2)
df2 = pd.DataFrame(results2.records)
df2.info()

results3 = memory(sql3)
df3 = pd.DataFrame(results3.records)
df3.info()

results4 = memory(sql4)
df4 = pd.DataFrame(results4.records)
df4.info()

with st.expander("Check hourly activity"):
    st.altair_chart(alt.Chart(df)
        .mark_line()
        .encode(x='date:N', y='active_contracts:Q')
        .properties(width=1200,title='Hourly active contracts'))
    
    st.altair_chart(alt.Chart(df3)
        .mark_line()
        .encode(x='date:N', y='new_contracts:Q')
        .properties(width=1200,title='Hourly new contracts'))

with st.expander("Check daily activity"):
    st.altair_chart(alt.Chart(df2)
        .mark_line()
        .encode(x='date:N', y='active_contracts:Q')
        .properties(width=1200,title='Daily active contracts'))
    
    st.altair_chart(alt.Chart(df4)
        .mark_line()
        .encode(x='date:N', y='new_contracts:Q')
        .properties(width=1200,title='Daily new contracts'))    
    
    

st.subheader('3. Transactions and fees')
st.markdown('**Methods:**')
st.write('In this analysis we will focus on Near transactions and fees. More specifically, we will analyze the following data:')
st.markdown('● Hourly transactions.')
st.markdown('● Daily transactions.')
st.markdown('● Hourly fees.')
st.markdown('● Daily fees.')
st.markdown('● Hourly gas paid.')
st.markdown('● Daily gas paid.')
st.write('')

sql="""
SELECT
trunc(x.block_timestamp,'hour') as date,
count(distinct x.tx_hash) as transactions,
count(distinct x.tx_signer) as active_users,
transactions/active_users as avg_tx_per_user,
sum(transaction_fee/pow(10,24)) as fees,
avg(transaction_fee/pow(10,24)) as avg_tx_fee,
sum(gas_used/pow(10,12)) as gas,
avg(gas_used/pow(10,12)) as avg_gas
  from near.core.fact_transactions x
  where x.block_timestamp>=current_date-INTERVAL '1 WEEK'
  group by 1


"""

sql2="""
SELECT
trunc(x.block_timestamp,'day') as date,
count(distinct x.tx_hash) as transactions,
count(distinct x.tx_signer) as active_users,
transactions/active_users as avg_tx_per_user,
sum(transaction_fee/pow(10,24)) as fees,
avg(transaction_fee/pow(10,24)) as avg_tx_fee,
sum(gas_used/pow(10,12)) as gas,
avg(gas_used/pow(10,12)) as avg_gas
  from near.core.fact_transactions x
  where x.block_timestamp>=current_date-INTERVAL '1 WEEK'
  group by 1

"""

st.experimental_memo(ttl=50000)
def memory(code):
    data=sdk.query(code)
    return data

results = memory(sql)
df = pd.DataFrame(results.records)
df.info()

results2 = memory(sql2)
df2 = pd.DataFrame(results2.records)
df2.info()

with st.expander("Check hourly activity"):
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])

    fig1.add_trace(go.Bar(x=df['date'],
                    y=df['fees'],
                    name='NEAR',
                    marker_color='rgb(250, 180, 10)'
                    , yaxis='y'))
    
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])

    fig2.add_trace(go.Bar(x=df['date'],
                    y=df['gas'],
                    name='Peta',
                    marker_color='rgb(10, 180, 250)'
                    , yaxis='y'))
    st.plotly_chart(fig1, theme="streamlit", use_container_width=True)
    st.plotly_chart(fig2, theme="streamlit", use_container_width=True)


with st.expander("Check daily activity"):
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])

    fig1.add_trace(go.Bar(x=df2['date'],
                    y=df2['fees'],
                    name='NEAR',
                    marker_color='rgb(250, 180, 10)'
                    , yaxis='y'))
    
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])

    fig2.add_trace(go.Bar(x=df2['date'],
                    y=df2['gas'],
                    name='Peta',
                    marker_color='rgb(10, 180, 250)'
                    , yaxis='y'))
    st.plotly_chart(fig1, theme="streamlit", use_container_width=True)
    st.plotly_chart(fig2, theme="streamlit", use_container_width=True)

# In[8]:


st.subheader("4. Proposed metric: total NEAR staked and number of validators")
st.markdown('**Methods:**')
st.write('In this analysis we will focus on Near staking. More specifically, we will analyze the following data:')
st.markdown('● Hourly NEAR staked')
st.markdown('● Daily NEAR staked')
st.markdown('● Hourly active validators staked')
st.markdown('● Daily active validators staked')
st.write('')
st.write('I have added this metric because I think is the most importnt to know about staking sector. I think it is a good metric to measure how decentralized is the ecosystem.')


sql="""
WITH
staking as (
SELECT tx_hash
FROM near.core.fact_actions_events_function_call
WHERE method_name in ('deposit_and_stake','stake','stake_all') and block_timestamp>=current_date-INTERVAL '3 MONTHS'
), stakes as (
SELECT
block_timestamp, tx_hash as tx, tx_receiver as validator, tx_signer as delegator,
tx:actions[0]:FunctionCall:deposit/pow(10,24) near_staked
FROM near.core.fact_transactions
WHERE tx_hash in (select * from staking) and block_timestamp>=current_date-INTERVAL '3 MONTHS'
),
monthly as (
SELECT
trunc(block_timestamp,'hour') as months, tx, validator, near_staked
FROM stakes WHERE near_staked is not null
),
totals as (
SELECT
months, sum(near_staked) as month_near_staked, sum(month_near_staked) over (order
by months)as total_near_staked
from monthly
group by 1 order by 1
),
ranking as (
SELECT
months, validator, count(distinct tx) as txs, sum(near_staked) as total_near_delegated,
sum(total_near_delegated) over (partition by validator order by months) as cumulative_near_delegated
FROM monthly
group by 1,2
)
select
x.months as date, total_near_staked,
count(distinct validator) as n_validators
from totals x
join ranking y on x.months=y.months
where x.months>=current_date-INTERVAL '1 WEEK'
group by 1,2
order by 1 asc
"""

sql2="""
WITH
staking as (
SELECT tx_hash
FROM near.core.fact_actions_events_function_call
WHERE method_name in ('deposit_and_stake','stake','stake_all') and block_timestamp>=current_date-INTERVAL '3 MONTHS'
), stakes as (
SELECT
block_timestamp, tx_hash as tx, tx_receiver as validator, tx_signer as delegator,
tx:actions[0]:FunctionCall:deposit/pow(10,24) near_staked
FROM near.core.fact_transactions
WHERE tx_hash in (select * from staking) and block_timestamp>=current_date-INTERVAL '3 MONTHS'
),
monthly as (
SELECT
trunc(block_timestamp,'day') as months, tx, validator, near_staked
FROM stakes WHERE near_staked is not null
),
totals as (
SELECT
months, sum(near_staked) as month_near_staked, sum(month_near_staked) over (order
by months)as total_near_staked
from monthly
group by 1 order by 1
),
ranking as (
SELECT
months, validator, count(distinct tx) as txs, sum(near_staked) as total_near_delegated,
sum(total_near_delegated) over (partition by validator order by months) as cumulative_near_delegated
FROM monthly
group by 1,2
)
select
x.months as date, total_near_staked,
count(distinct validator) as n_validators
from totals x
join ranking y on x.months=y.months
where x.months>=current_date-INTERVAL '1 WEEK'
group by 1,2
order by 1 asc
"""

results = memory(sql)
df = pd.DataFrame(results.records)
df.info()


results2 = memory(sql2)
df2 = pd.DataFrame(results2.records)
df2.info()

with st.expander("Check hourly activity"):
    st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='n_validators:Q')
        .properties(width=1200,title='Hourly active validators'))
    
    st.altair_chart(alt.Chart(df)
        .mark_line()
        .encode(x='date:N', y='total_near_staked:Q')
        .properties(width=1200,title='Hourly total NEAR staked'))

with st.expander("Check daily activity"):
    st.altair_chart(alt.Chart(df2)
        .mark_line()
        .encode(x='date:N', y='n_validators:Q')
        .properties(width=1200,title='Daily active validators'))
    
    st.altair_chart(alt.Chart(df2)
        .mark_line()
        .encode(x='date:N', y='total_near_staked:Q')
        .properties(width=1200,title='Daily total NEAR staked'))


st.markdown('This dashboard has been done by _Cristina Tintó_ powered by **Flipside Crypto** data and carried out for **MetricsDAO**.')


# In[ ]:




