import sys
sys.path.append("../")
from src.ATMController import ATMController

# from ATMController import ATMController
class TestLogger():
    def __init__(self):
        self.log=""
    def log_fun(self,s):
        self.log+=s+"\n"
    def print_log(self):
        return self.log
    def clear_log(self):
        self.log=""

# TestBankAPI: Assume all function is well working
#               : all return True default
class TestBankAPI():
    def __init__(self, cid,pin,acc_list,bal_list):
        self.cid=cid
        self.pin=pin
        self.account_list=acc_list
        self.balance_list=bal_list
        
        self.is_logined=False
        self.account=-1
    
    def logout(self):
        self.is_logined=False
        self.account=-1
        return True
    def is_login(self):
        return self.is_logined
    def pin_login(self,cid,pin):
        if cid==self.cid and pin==self.pin:
            self.is_logined=True
        return (True,self.is_logined)
    def get_account_list(self):
        return (True,self.account_list)
    def set_account(self,acc):
        if acc<0:
            return (True,False)
        if acc<len(self.account_list):
            self.account=acc
            return (True,True)
        return (False,False)
    def get_account_balance(self):
        if self.account>=0 and self.account<len(self.account_list):
            return (True,self.balance_list[self.account])
        return (False,0)
    def deposit(self,val):
        if self.account>=0 and self.account<len(self.account_list):
            if val>0:
                self.balance_list[self.account]+=val
                return (True,True)
            else:
                return (True,False)
        return (False,False)
        
    def withdraw(self,val):
        if val<=0:
            return (True,False)
        if self.account>=0 and self.account<len(self.account_list):
            if self.balance_list[self.account]<val:
                return (True,False)
            else:
                self.balance_list[self.account]-=val
                return (True,True)
        return (False,False)

# TestCardReader: Assume all function is well working
#               : all return True default
class TestCardReader():
    def __init__(self,cid_init="1234"):
        self.cid="" # "12345678"
        self.cid_init=cid_init
        self.en=False
    def enable(self):
        self.en=True
        return True
    def disable(self):
        self.cid=""
        self.en=False
        return True
    def check_card_in(self):
        return self.en and len(self.cid)>0
    def check_card_valid(self):
        return self.en and self.cid[:4]==self.cid_init
    def eject_card(self):
        # self.cid=""
        return self.cid==""
    def get_card_info(self):
        return self.cid if self.en else ""
    def insert_card(self, cid):
        if self.en:
            self.cid=cid
            return True
        return False
    def remove_card(self):
        if self.en:
            self.cid=""
            return True
        return False

# TestUI: Assume all function is well working
#       : all return True default
class TestUI():
    def __init__(self, pin_read="9090", acc_sel=0, opt_sel=0, bal_sel=True, dep_sel=True, withdraw_val=10):
        self.current_window=None
        self.acc_len=None
        self.acc_sel=acc_sel
        self.opt_sel=opt_sel
        self.bal_sel=bal_sel
        self.dep_cancel=False
        self.dep_sel=dep_sel
        self.withdraw_val=withdraw_val
        self.withdraw_max=None
        self.pin_read= pin_read # assume 4 digits, "": cancel
        
        self.ret=True
        
    def show_main(self):
        self.current_window="main"
        return True
    def show_loading(self):
        self.current_window="loading"
        return True
    def show_card_eject(self, msg):
        self.current_window="card_eject:"+msg
        return True
    def show_money_eject(self):
        self.current_window="money_eject"
        return True
    def show_pin_read(self):
        self.current_window="pin_read"
        return True
    def show_account_list(self, acc_list):
        self.acc_len=len(acc_list)
        self.current_window="account_list:"+str(len(acc_list))
        return True
    def show_option_select(self):
        self.current_window="option_select"
        return True
    def show_balance_select(self, balance):
        self.current_window="balance_select"
        return True
    def show_deposit_ready(self):
        self.current_window="deposit_ready"
        return True
    def show_deposit_select(self, deposit_val):
        self.current_window="deposit_select:"+str(deposit_val)
        return True
    def show_withdraw(self, withdraw_max):
        self.withdraw_max=withdraw_max
        self.current_window="withdraw:"+str(withdraw_max)
        return True
    
    def get_pin_read(self):
        ret=self.ret
        self.ret=True
        return (ret,self.pin_read)
    def get_account_select(self):
        ret=self.ret
        self.ret=True
        sel = self.acc_sel # return index, -1: cancel
        return (ret,sel)
    def get_option_select(self):
        ret=self.ret
        self.ret=True
        sel = self.opt_sel # 0: see balance, 1: deposit, 2: withdraw, -1: cancel
        return (ret,sel)
    def get_balance_select(self):
        ret=self.ret
        self.ret=True
        sel = self.bal_sel # True: done, False: cancel
        return (ret,sel)
    def get_deposit_ready(self):
        ret=self.ret
        self.ret=True
        sel = not self.dep_cancel # cancel only, ret=True, sel=False: cancel
        return (ret,sel)
    def get_deposit_select(self):
        ret=self.ret
        self.ret=True
        sel = self.dep_sel # True: deposit, False: cancel
        return (ret,sel)
    def get_withdraw_select(self):
        ret=self.ret
        self.ret=True
        val = self.withdraw_val # int, <0: cancel, 0: 0 err, max>sel>0: withdraw
        return (ret,val)


# TestCashBin: Assume all function is well working
#            : all return True default
class TestCashBin():
    def __init__(self,bin_cur=1000,bin_cap=2000):
        self.current=bin_cur
        self.capacity=bin_cap
        self.is_slot_open=None
        self.slot_money=0
    def init(self):
        self.is_slot_open=False
        self.slot_money=0
        return True
    def is_open_slot(self):
        return self.is_slot_open
    def open_slot(self):
        self.is_slot_open=True
        return True
    def is_slot_empty(self):
        return self.slot_money==0
    def close_slot(self):
        self.is_slot_open=False
        return True
    def get_bin_amounts(self):
        return (True,self.current)
    def count_slot(self):
        return (True,self.slot_money)
    def deposit(self):
        cur = self.slot_money+self.current
        if cur>self.capacity:
            return False
        self.current = cur
        self.slot_money = 0
        return True
    def withdraw(self, val):
        if val>self.current:
            return False
        self.current -= val
        self.slot_money = val
        return True
     
class TestATMController(ATMController):
    def get_stages(self):
        return self._stages.keys()
    def get_stage(self):
        return self._stage
    
class ATMControllerTester():
    def __init__(self, cid,pin,acc_list,bal_list,bin_cur,bin_cap):
        cid_init=cid[:4]
        pin_read=pin
        
        self.cid=cid
        self.pin=pin
        self.acc_list=acc_list
        self.bal_list=bal_list
        self.cid_init=cid_init
        self.pin_read=pin_read
        self.bin_cur=bin_cur
        self.bin_cap=bin_cap
        
        self.tlogger=TestLogger()
        self.bank_api=TestBankAPI(cid,pin,acc_list,bal_list)
        self.card_reader=TestCardReader(cid_init=cid_init)
        self.ui=TestUI(pin_read=pin_read)
        self.cash_bin=TestCashBin(bin_cur=bin_cur,bin_cap=bin_cap)
        
        self.atm_con=None
        
    def print_log(self):
        print("\nlogs:")
        print(self.tlogger.print_log())
    def create_test_con(self, prefix=""):
        indent=""
        for i in range(len(prefix)):
            indent+=" "
        print("\n{}create_test_con...".format(prefix))
        self.atm_con=TestATMController(self.bank_api, self.card_reader, self.ui, self.cash_bin, log_fun=self.tlogger.log_fun)
        print("{}stages: {}".format(indent,self.atm_con.get_stages()))
        print("{}next state: {}".format(indent,self.atm_con.get_stage()))
        print("{}done".format(indent))
    def test_step(self,stage,prefix=""):
        indent=""
        for i in range(len(prefix)):
            indent+=" "
        print("\n{}test_{}...".format(prefix,stage))
        state=self.atm_con.get_stage()
        if state != stage:
            print("{}failed!! state[{}] is not {}".format(indent,state,stage))
            return
        ret = self.atm_con.run_step()
        print("{}next state: {}".format(indent,self.atm_con.get_stage()))
        if ret:
            print("{}test_{}: failed!! ret={}".format(indent,stage,ret))
        else:
            print("{}test_{}: pass!!".format(indent,stage))
    
    
def test_init_to_main(tester):
    tester.create_test_con(prefix="0.")
    tester.test_step("init","0.")
    
def test_main_to_account_select(tester,cid,pin,acc_sel,prefix=""):
    # print("\ncid0:",tester.atm_con._card_reader.cid)
    tester.test_step("main",prefix+"1.")
    tester.card_reader.insert_card(cid) # insert card to card slot with right cid
    #print("\ncid1:",tester.atm_con._card_reader.cid)
    tester.test_step("main",prefix+"2.")
    tester.test_step("card_check",prefix+"3.")
    tester.ui.pin_read=pin # right pid
    tester.test_step("pin_read",prefix+"4.")
    tester.test_step("pin_login",prefix+"5.")
    tester.ui.acc_sel=acc_sel # i-th account
    tester.test_step("account_select",prefix+"6.")
    
def test_see_balance(tester,prefix=""):
    tester.ui.ret=False # skip user input
    tester.test_step("option_select",prefix+"7.")
    tester.ui.opt_sel=0 # see balance
    tester.test_step("option_select",prefix+"8.")
    tester.test_step("balance_get",prefix+"9.")
    tester.ui.ret=False # skip user input
    tester.test_step("balance_select",prefix+"10.")
    tester.ui.bal_sel=True # see balnce done
    tester.test_step("balance_select",prefix+"11.")
    
    tester.test_step("card_eject",prefix+"12.")
    tester.card_reader.remove_card() # remove card from card slot
    tester.test_step("card_eject",prefix+"13.")
    
def test_deposit(tester,prefix=""):
    tester.ui.opt_sel=1 # deposit
    tester.test_step("option_select",prefix+"7.")
    tester.ui.ret=False # skip user input
    tester.cash_bin.slot_money=0 # not insert money yet
    tester.test_step("deposit_ready",prefix+"8.")
    tester.ui.dep_cancel=False # do not cancel
    tester.cash_bin.slot_money=300 # insert money:300 dollars
    tester.test_step("deposit_ready",prefix+"9.")
    tester.test_step("deposit_count",prefix+"10.")
    tester.ui.ret=False # skip user input
    tester.test_step("deposit_select",prefix+"11.")
    tester.ui.dep_sel=True# True: deposit, False: cancel
    tester.test_step("deposit_select",prefix+"12.")
    print("\n",prefix,"bals_before:",tester.bank_api.balance_list)
    tester.test_step("deposit_final",prefix+"13.")
    print("\n",prefix,"bals_after:",tester.bank_api.balance_list)
    
    tester.test_step("card_eject",prefix+"14.")
    tester.card_reader.remove_card() # remove card from card slot
    tester.test_step("card_eject",prefix+"15.")
    
def test_withdraw(tester,prefix=""):
    tester.ui.opt_sel=2 # withdraw
    tester.test_step("option_select",prefix+"7.")
    tester.test_step("withdraw_get",prefix+"8.")
    tester.ui.ret=False # skip user input
    tester.test_step("withdraw_select",prefix+"9.")
    tester.ui.withdraw_val=200 # skip user input
    tester.test_step("withdraw_select",prefix+"10.")
    print("\n",prefix,"bals_before:",tester.bank_api.balance_list)
    tester.test_step("withdraw_final",prefix+"11.")
    print("\n",prefix,"bals_after:",tester.bank_api.balance_list)
    
    print("\n",prefix,"slot_money:",tester.cash_bin.slot_money)
    tester.test_step("card_eject",prefix+"12.")
    tester.card_reader.remove_card() # remove card from card slot
    tester.test_step("card_eject",prefix+"13.")
    tester.test_step("money_eject",prefix+"14.")
    tester.cash_bin.slot_money=0 # not insert money yet
    tester.test_step("money_eject",prefix+"15.")
    
def test_all_once(tester,cid,pin):
    # 0. init controller
    test_init_to_main(tester)
    
    # 1. test see balance
    print("\n\n1.test_see_balance")
    acc_sel=0 # 0th account
    test_main_to_account_select(tester,cid,pin,acc_sel,prefix="1.")
    test_see_balance(tester,prefix="1.")
    
    # 2. test deposit
    print("\n\n2.test_deposit")
    acc_sel=1 # 1th account
    test_main_to_account_select(tester,cid,pin,acc_sel,prefix="2.")
    test_deposit(tester,prefix="2.")
    
    # 2. test withdraw
    print("\n\n3.test_withdraw")
    acc_sel=2 # 2th account
    test_main_to_account_select(tester,cid,pin,acc_sel,prefix="3.")
    test_withdraw(tester,prefix="3.")
    
########################################################################
# if you want more test functions:
# add more test functions at below...
# def test_fun(tester,*args,**kwargs):
#     return
########################################################################
if __name__ == "__main__":
    print("test_ATMController")
    
    cid="12345678"
    pin="9090"
    acc_list=["12123456","34567890","78907890","12348765","98765432"]
    bal_list=[0,100,500,1500,2500]
    bin_cur=1000
    bin_cap=2000

    print("test_all_once")
    tester=ATMControllerTester(cid,pin,acc_list,bal_list,bin_cur,bin_cap)
    test_all_once(tester,cid,pin)
    tester.print_log()
    print("Done")
