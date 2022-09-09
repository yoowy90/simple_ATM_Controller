import sys
sys.path.append("../")

class ATMController():
    def __init__(self, bank_api, card_reader, ui, cash_bin, log_fun=None):
        self._bank_api=bank_api
        self._card_reader=card_reader
        self._ui=ui
        self._cash_bin=cash_bin
        self._log_fun=log_fun
        
        self._stages={
            "init": self._stage_init,
            "main":self._stage_main,
            "card_check":self._stage_card_check,
            "card_eject":self._stage_card_eject,
            "money_eject":self._stage_money_eject,
            "pin_read":self._stage_pin_read,
            "pin_login":self._stage_pin_login,
            "account_select":self._stage_account_select,
            "option_select":self._stage_option_select,
            "balance_get":self._stage_balance_get,
            "balance_select":self._stage_balance_select,
            "deposit_ready":self._stage_deposit_ready,
            "deposit_count":self._stage_deposit_count,
            "deposit_select":self._stage_deposit_select,
            "deposit_final":self._stage_deposit_final,
            "withdraw_get":self._stage_withdraw_get,
            "withdraw_select":self._stage_withdraw_select,
            "withdraw_final":self._stage_withdraw_final
        }
        self._stage="init"
        self._pin=None
        self._withdraw_val=None
        self._msg=None
        
        # self._stage_init()
        
    def run_step(self):
        return self._stages[self._stage]()
    
    def _log(self,s):
        if self._log_fun is not None:
            return self._log_fun(s)
    
    def loop(self):
        en=True
        while(en):
            en = self.run_step()
        return en
        
    def _stage_init(self): # init other modules
        self._bank_api.logout()
        self._card_reader.disable()
        self._cash_bin.init()
        
        if self._bank_api.is_login():
            self._log("stage_init: bank_api.is_login failure")
            return 1
        if self._card_reader.check_card_in():
            self._log("stage_init: card_reader.check_card_in failure")
            return 2
        if self._cash_bin.is_open_slot():
            self._log("stage_init: cash_bin.is_open_slot failure")
            return 3
        
        if not self._card_reader.enable():
            self._log("stage_init: card_reader.enable failure")
            return 4
        
        self._ui.show_main()
        self._stage="main"
        self._log("stage_init: Done")
        return 0
    
    def _stage_main(self): # main base stage: check card in
        if self._bank_api.is_login():
            self._log("stage_main: bank_api.is_login failure")
            return 5
        if self._cash_bin.is_open_slot():
            self._log("stage_main: cash_bin.is_open_slot failure")
            return 6
        
        # check card in
        if self._card_reader.check_card_in():
            self._ui.show_loading()
            self._stage="card_check"
            
        self._log("stage_main: Done")
        return 0
    
    def _stage_card_check(self): # card check stage: check card is valid
        if self._bank_api.is_login():
            self._log("stage_card_check: bank_api.is_login failure")
            return 7
        if self._cash_bin.is_open_slot():
            self._log("stage_card_check: cash_bin.is_open_slot failure")
            return 8
        
        if self._card_reader.check_card_valid():
            self._ui.show_pin_read()
            self._stage="pin_read"
        else:
            msg="Card is not valid"
            self._msg=msg
            self._ui.show_card_eject(msg)
            self._stage="card_eject"

        self._log("stage_card_check: Done")
        return 0
    
    def _stage_card_eject(self): # ejact card with msg
        if self._cash_bin.is_open_slot():
            self._log("stage_card_eject: cash_bin.is_open_slot failure")
            return 9
        
        self._card_reader.eject_card()
        if not self._card_reader.check_card_in():
            # slot is closed with money: return
            if not self._cash_bin.is_slot_empty():
                self._ui.show_money_eject()
                self._cash_bin.open_slot()
                self._stage="money_eject"
            else: # slot is empty
                self._ui.show_main()
                self._stage="main"
            
        # self._log("stage_card_eject: msg [{}]".format(self._msg))
        self._log("stage_card_eject: Done")
        return 0
    
    def _stage_money_eject(self): # ejact money
        if not self._cash_bin.is_open_slot():
            self._log("stage_money_eject: cash_bin.is_open_slot failure")
            return 10
        if self._card_reader.check_card_in():
            self._log("stage_money_eject: card_reader.eject_card failure")
            return 11
        
        # slot is empty
        if self._cash_bin.is_slot_empty():
            self._cash_bin.close_slot()
            self._ui.show_main()
            self._stage="main"
            
        self._log("stage_money_eject: Done")
        return 0
    
    def _stage_pin_read(self): # read pin
        if self._bank_api.is_login():
            self._log("stage_pin_read: bank_api.is_login failure")
            return 12
        if not self._card_reader.check_card_in():
            self._log("stage_pin_read: card_reader.check_card_in failure")
            return 13
        if self._cash_bin.is_open_slot():
            self._log("stage_pin_read: cash_bin.is_open_slot failure")
            return 14
        
        ret,pin=self._ui.get_pin_read()
        if ret: # True: if return get, False: not arrival
            if len(pin)==0: # canceled
                msg="Canceled"
                self._msg=msg
                self._ui.show_card_eject(msg)
                self._stage="card_eject"
            else:
                self._pin=pin
                self._ui.show_loading()
                self._stage="pin_login"
            
        self._log("stage_pin_read: Done")
        return 0
    
    def _stage_pin_login(self): # check pin is valid and login to bank db
        if self._bank_api.is_login():
            self._log("stage_pin_login: bank_api.is_login failure")
            return 15
        if not self._card_reader.check_card_in():
            self._log("stage_pin_login: card_reader.check_card_in failure")
            return 16
        if self._cash_bin.is_open_slot():
            self._log("stage_pin_login: cash_bin.is_open_slot failure")
            return 17
        
        pin=self._pin
        self._pin=None
        cid=self._card_reader.get_card_info()
        ret,res = self._bank_api.pin_login(cid,pin)
        if not ret:
            self._log("stage_pin_login: bank_api.pin_login failure")
            return 18
        elif res:
            ret, acc_list = self._bank_api.get_account_list()
            if not ret:
                self._log("stage_pin_login: bank_api.get_account_list failure")
                return 19
            if len(acc_list)==0:
                msg="There are no activated accounts"
                self._msg=msg
                self._ui.show_card_eject(msg)
                self._stage="card_eject"
            else:
                self._ui.show_account_list(acc_list)
                self._stage="account_select"
        else:
            msg="PIN nunmber is wrong"
            self._msg=msg
            self._ui.show_card_eject(msg)
            self._stage="card_eject"
            
        self._log("stage_pin_read: Done")
        return 0
    
    def _stage_account_select(self): # show accounts. get selected account
        if not self._bank_api.is_login():
            self._log("stage_account_select: bank_api.is_login failure")
            return 20
        if not self._card_reader.check_card_in():
            self._log("stage_account_select: card_reader.check_card_in failure")
            return 21
        if self._cash_bin.is_open_slot():
            self._log("stage_account_select: cash_bin.is_open_slot failure")
            return 22
        
        ret, acc = self._ui.get_account_select()
        if ret: # True: if return get, False: not arrival
            if acc < 0: # canceled
                msg="Canceled"
                self._msg=msg
                self._ui.show_card_eject(msg)
                self._stage="card_eject"
            else:
                ret,res = self._bank_api.set_account(acc)
                if not ret:
                    self._log("stage_account_select: bank_api.set_account failure")
                    return 23
                elif res:
                    self._ui.show_option_select()
                    self._stage="option_select"
                else: # canceled
                    msg="Canceled"
                    self._msg=msg
                    self._ui.show_card_eject(msg)
                    self._stage="card_eject"
        
        self._log("stage_account_select: Done")
        return 0
    
    def _stage_option_select(self): # account selected. list options: balance, deposit, withdraw
        if not self._bank_api.is_login():
            self._log("stage_option_select: bank_api.is_login failure")
            return 24
        if not self._card_reader.check_card_in():
            self._log("stage_option_select: card_reader.check_card_in failure")
            return 25
        if self._cash_bin.is_open_slot():
            self._log("stage_option_select: cash_bin.is_open_slot failure")
            return 26
        
        ret,opt = self._ui.get_option_select()
        if ret: # True: if return get, False: not arrival
            if opt == 0: # see balance
                self._ui.show_loading()
                self._stage="balance_get"
            elif opt == 1: # deposit
                self._ui.show_deposit_ready()
                self._cash_bin.open_slot()
                self._stage="deposit_ready"
            elif opt == 2: # withdraw
                self._ui.show_loading()
                self._stage="withdraw_get"
            else: # canceled
                msg="Canceled"
                self._msg=msg
                self._ui.show_card_eject(msg)
                self._stage="card_eject"
        
        self._log("stage_option_select: Done")
        return 0
    
    def _stage_balance_get(self): # get balance
        if not self._bank_api.is_login():
            self._log("stage_balance_get: bank_api.is_login failure")
            return 27
        if not self._card_reader.check_card_in():
            self._log("stage_balance_get: card_reader.check_card_in failure")
            return 28
        if self._cash_bin.is_open_slot():
            self._log("stage_balance_get: cash_bin.is_open_slot failure")
            return 29
        
        ret,balance = self._bank_api.get_account_balance()
        if not ret:
            self._log("stage_balance_get: bank_api.get_account_balance failure")
            return 30
        if not self._bank_api.logout():
            self._log("stage_balance_get: bank_api.logout failure")
            return 31
        
        self._ui.show_balance_select(balance)
        self._stage="balance_select"
        
        self._log("stage_balance_get: Done")
        return 0
    
    def _stage_balance_select(self): # show balance
        if self._bank_api.is_login():
            self._log("stage_balance_select: bank_api.is_login failure")
            return 32
        if not self._card_reader.check_card_in():
            self._log("stage_balance_select: card_reader.check_card_in failure")
            return 33
        if self._cash_bin.is_open_slot():
            self._log("stage_balance_select: cash_bin.is_open_slot failure")
            return 34
        
        ret,opt = self._ui.get_balance_select()
        if ret: # True: if return get, False: not arrival
            if opt: # done
                msg="Thank you"
            else: # canceled
                msg="Canceled"
            self._msg=msg
            self._ui.show_card_eject(msg)
            self._stage="card_eject"
        
        self._log("stage_balance_select: Done")
        return 0
    
    def _stage_deposit_ready(self): # deposit ready: show contents to ui and get money to deposit from slot
        if not self._bank_api.is_login():
            self._log("stage_deposit_ready: bank_api.is_login failure")
            return 35
        if not self._card_reader.check_card_in():
            self._log("stage_deposit_ready: card_reader.check_card_in failure")
            return 36
        if not self._cash_bin.is_open_slot():
            self._log("stage_deposit_ready: cash_bin.is_open_slot failure")
            return 37
        
        # Don't care other object in the slot, if that: failure...
        # Don't care timeout
        ret,opt = self._ui.get_deposit_ready()
        # ret = True: if return get, False: not arrival
        if ret:
            if not opt: # canceled
                self._cash_bin.close_slot()
                msg="Canceled"
                self._msg=msg
                self._ui.show_card_eject(msg)
                self._stage="card_eject"
            else: # not yet canceled
                if not self._cash_bin.is_slot_empty():
                    # to deposit
                    self._cash_bin.close_slot()
                    self._ui.show_loading()
                    self._stage="deposit_count"
        elif not self._cash_bin.is_slot_empty():
            # to deposit
            self._cash_bin.close_slot()
            self._ui.show_loading()
            self._stage="deposit_count"

        self._log("stage_deposit_ready: Done")
        return 0
    
    def _stage_deposit_count(self): # deposit count: count money in slot
        if not self._bank_api.is_login():
            self._log("stage_deposit_count: bank_api.is_login failure")
            return 38
        if not self._card_reader.check_card_in():
            self._log("stage_deposit_count: card_reader.check_card_in failure")
            return 39
        if self._cash_bin.is_open_slot():
            self._log("stage_deposit_count: cash_bin.is_open_slot failure")
            return 40
        
        ret,cnt = self._cash_bin.count_slot()
        if not ret: # bin is full: money can not store
            msg="The ATM bin is full"
            self._msg=msg
            self._ui.show_card_eject(msg)
            self._stage="card_eject"
        elif not cnt: # money is 0 dollars
            msg="The deposited money is 0 dollars"
            self._msg=msg
            self._ui.show_card_eject(msg)
            self._stage="card_eject"
        else: # to deposit_select
            self._ui.show_deposit_select(cnt)
            self._stage="deposit_select"

        self._log("stage_deposit_count: Done")
        return 0
    
    def _stage_deposit_select(self): # deposit decision: confirm deposit
        if not self._bank_api.is_login():
            self._log("stage_deposit_select: bank_api.is_login failure")
            return 41
        if not self._card_reader.check_card_in():
            self._log("stage_deposit_select: card_reader.check_card_in failure")
            return 42
        if self._cash_bin.is_open_slot():
            self._log("stage_deposit_select: cash_bin.is_open_slot failure")
            return 43
        
        ret,opt = self._ui.get_deposit_select()
        if ret: # True: if return get, False: not arrival
            if opt: # done
                self._ui.show_loading()
                self._stage="deposit_final"
            else: # canceled
                msg="Canceled"
                self._ui.show_card_eject(msg)
                self._stage="card_eject"
            
        self._log("stage_deposit_select: Done")
        return 0
    
    def _stage_deposit_final(self): # deposit decision: confirm deposit
        if not self._bank_api.is_login():
            self._log("stage_deposit_final: bank_api.is_login failure")
            return 44
        if not self._card_reader.check_card_in():
            self._log("stage_deposit_final: card_reader.check_card_in failure")
            return 45
        if self._cash_bin.is_open_slot():
            self._log("stage_deposit_final: cash_bin.is_open_slot failure")
            return 46

        # deposit the money
        ret,cnt = self._cash_bin.count_slot()
        ret,res = self._bank_api.deposit(cnt)
        if not ret:
            self._log("stage_deposit_final: bank_api.deposit failure")
            return 47
        elif not res: # canceled
            msg="Canceled"
        # save money to cash bin
        elif not self._cash_bin.deposit():
            self._log("stage_deposit_final: cash_bin.save_money failure")
            return 48
        else: # finished
            msg="Thank you"
            
        if not self._bank_api.logout():
            self._log("stage_deposit_final: bank_api.logout failure")
            return 49
        
        self._msg=msg
        self._ui.show_card_eject(msg)
        self._stage="card_eject"
        self._log("stage_deposit_final: Done")
        return 0
    
    def _stage_withdraw_get(self): # withdraw get: get balance
        if not self._bank_api.is_login():
            self._log("stage_withdraw_get: bank_api.is_login failure")
            return 50
        if not self._card_reader.check_card_in():
            self._log("stage_withdraw_get: card_reader.check_card_in failure")
            return 51
        if self._cash_bin.is_open_slot():
            self._log("stage_withdraw_get: cash_bin.is_open_slot failure")
            return 52
        
        ret,balance = self._bank_api.get_account_balance()
        if not ret:
            self._log("stage_withdraw_get: bank_api.get_account_balance failure")
            return 53
        ret,amounts = self._cash_bin.get_bin_amounts()
        if not ret:
            self._log("stage_withdraw_get: cash_bin.get_bin_amounts failure")
            return 54
        
        # show withdraw selection menu with max amounts
        self._ui.show_withdraw(min(balance,amounts))
        self._stage="withdraw_select"
        
        self._log("stage_withdraw_get: Done")
        return 0
    
    def _stage_withdraw_select(self): # show balance
        if not self._bank_api.is_login():
            self._log("stage_withdraw_select: bank_api.is_login failure")
            return 55
        if not self._card_reader.check_card_in():
            self._log("stage_withdraw_select: card_reader.check_card_in failure")
            return 56
        if self._cash_bin.is_open_slot():
            self._log("stage_withdraw_select: cash_bin.is_open_slot failure")
            return 57
        
        ret,val = self._ui.get_withdraw_select()
        if ret: # True: if return get, False: not arrival
            if val<0: # canceled
                msg="Canceled"
                self._msg=msg
                self._ui.show_card_eject(msg)
                self._stage="card_eject"
            if val==0: # 0 value
                msg="Withdraw: 0 Dollars"
                self._msg=msg
                self._ui.show_card_eject(msg)
                self._stage="card_eject"
            else: # withdraw_final
                self._ui.show_loading()
                self._withdraw_val=val
                self._stage="withdraw_final"
                
        self._log("stage_withdraw_select: Done")
        return 0
    
    def _stage_withdraw_final(self): # show balance
        if not self._bank_api.is_login():
            self._log("stage_withdraw_final: bank_api.is_login failure")
            return 58
        if not self._card_reader.check_card_in():
            self._log("stage_withdraw_final: card_reader.check_card_in failure")
            return 59
        if self._cash_bin.is_open_slot():
            self._log("stage_withdraw_final: cash_bin.is_open_slot failure")
            return 60
                
        # request withdraw
        val=self._withdraw_val
        self._withdraw_val=None
        ret,res = self._bank_api.withdraw(val)
        if not ret:
            self._log("stage_withdraw_final: bank_api.withdraw failure")
            return 61
        if not res: # canceled
            msg="Canceled"
        # load money from cash bin
        elif not self._cash_bin.withdraw(val):
            self._log("stage_withdraw_final: cash_bin.withdraw failure")
            return 62
        else: # Done
            msg="Thank you"
            
        if not self._bank_api.logout():
            self._log("stage_withdraw_final: bank_api.logout failure")
            return 63
        
        self._msg=msg
        self._ui.show_card_eject(msg)
        self._stage="card_eject"
        self._log("stage_withdraw_final: Done")
        return 0
    
# if __name__ == "__main__":
#     from src import bank_api, card_reader, ui, cash_bin
#     atmcon=ATMController(bank_api, card_reader, ui, cash_bin, log_fun=None)
#     atmcon.loop()
