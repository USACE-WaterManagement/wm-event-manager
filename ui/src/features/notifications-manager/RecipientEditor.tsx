import { useEffect, useMemo, useState } from "react";
import {
  Badge,
  Button,
  Dropdown,
  Input,
  Search,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  Text,
} from "@usace/groundwork";
import { FaPlus, FaXmark } from "react-icons/fa6";
import { HelpTip } from "../../shared/components/HelpTip";
import { useCdaUserLists } from "./api";

type AddRecipientMode = "manual" | "user-list";

interface RecipientEditorProps {
  office: string;
  availableOffices: string[];
  cdaUserListId: string;
  cdaUserListOffice: string;
  manualRecipients: string[];
  onCdaUserListChange: (office: string, userListId: string) => void;
  onManualRecipientsChange: (recipients: string[]) => void;
}

const isEmail = (value: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);

export const RecipientEditor = ({
  office,
  availableOffices,
  cdaUserListId,
  cdaUserListOffice,
  manualRecipients,
  onCdaUserListChange,
  onManualRecipientsChange,
}: RecipientEditorProps) => {
  const cdaUiRoot =
    import.meta.env.VITE_CDA_UI_ROOT ??
    (import.meta.env.DEV ? "http://localhost:5174/cwms-data" : "");
  const [addMode, setAddMode] = useState<AddRecipientMode | null>(null);
  const [manualEmail, setManualEmail] = useState("");
  const [manualError, setManualError] = useState("");
  const [userListSearch, setUserListSearch] = useState("");
  const [debouncedUserListSearch, setDebouncedUserListSearch] = useState("");
  const [userListOffice, setUserListOffice] = useState(
    cdaUserListOffice || office,
  );
  const userLists = useCdaUserLists(
    addMode === "user-list" ? userListOffice : undefined,
  );

  useEffect(() => {
    if (addMode === "user-list") {
      setUserListOffice(cdaUserListOffice || office);
    }
  }, [addMode, cdaUserListOffice, office]);

  useEffect(() => {
    const timer = window.setTimeout(
      () => setDebouncedUserListSearch(userListSearch.trim()),
      250,
    );
    return () => window.clearTimeout(timer);
  }, [userListSearch]);

  const selectedUserList = userLists.data?.find(
    (list) =>
      userListOffice === cdaUserListOffice &&
      list["user-list-id"] === cdaUserListId,
  );

  const orderedAvailableOffices = [
    userListOffice,
    ...availableOffices
      .filter((availableOffice) => availableOffice !== userListOffice)
      .sort(),
  ];

  const filteredUserLists = useMemo(() => {
    const search = debouncedUserListSearch.toLocaleLowerCase();
    const matches = search
      ? (userLists.data ?? []).filter((list) =>
          `${list["user-list-id"]} ${list.description ?? ""}`
            .toLocaleLowerCase()
            .includes(search),
        )
      : (userLists.data ?? []);
    return matches.slice(0, search ? 20 : 5);
  }, [debouncedUserListSearch, userLists.data]);

  const addManualRecipient = () => {
    const email = manualEmail.trim().toLocaleLowerCase();
    if (!isEmail(email)) {
      setManualError("Enter a valid email address.");
      return;
    }
    if (manualRecipients.includes(email)) {
      setManualError("That email address is already included.");
      return;
    }
    onManualRecipientsChange([...manualRecipients, email]);
    setManualEmail("");
    setManualError("");
  };

  const chooseUserList = (userListId: string) => {
    onCdaUserListChange(userListOffice, userListId);
    setAddMode(null);
    setUserListSearch("");
    setDebouncedUserListSearch("");
  };

  return (
    <section className="grid gap-3 rounded-lg border border-zinc-200 bg-white p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-1">
            <Text className="font-semibold text-zinc-950">Recipients</Text>
            <HelpTip title="Email recipients">
              Add individual email addresses or one office-scoped CDA user list.
              List membership is resolved by CDA each time an email is sent.
            </HelpTip>
          </div>
          <Text className="text-sm text-zinc-600">
            {manualRecipients.length + (cdaUserListId ? 1 : 0)} recipient
            {manualRecipients.length + (cdaUserListId ? 1 : 0) === 1
              ? " source"
              : " sources"}
          </Text>
        </div>
        <Button
          type="button"
          color="light"
          onClick={() => setAddMode((current) => current ?? "manual")}
        >
          <FaPlus aria-hidden="true" />
          Add recipient
        </Button>
      </div>

      <div className="max-h-56 overflow-auto rounded-lg border border-zinc-200">
        <Table className="min-w-full">
          <TableHead className="sticky top-0 z-10 bg-zinc-50">
            <TableRow>
              <TableHeader>Type</TableHeader>
              <TableHeader>Recipient</TableHeader>
              <TableHeader>
                <span className="sr-only">Actions</span>
              </TableHeader>
            </TableRow>
          </TableHead>
          <TableBody>
            {cdaUserListId && (
              <TableRow>
                <TableCell>
                  <Badge color="blue">CDA list</Badge>
                </TableCell>
                <TableCell>
                  <span className="font-medium">
                    {cdaUserListOffice} / {cdaUserListId}
                  </span>
                  {selectedUserList?.description && (
                    <span className="ml-2 text-sm text-zinc-600">
                      {selectedUserList.description}
                    </span>
                  )}
                </TableCell>
                <TableCell className="text-right">
                  <Button
                    type="button"
                    color="danger"
                    style="outline"
                    aria-label={`Remove CDA user list ${cdaUserListId}`}
                    onClick={() => onCdaUserListChange("", "")}
                  >
                    <FaXmark aria-hidden="true" />
                  </Button>
                </TableCell>
              </TableRow>
            )}
            {manualRecipients.map((email) => (
              <TableRow key={email}>
                <TableCell>
                  <Badge color="zinc">Email</Badge>
                </TableCell>
                <TableCell>{email}</TableCell>
                <TableCell className="text-right">
                  <Button
                    type="button"
                    color="danger"
                    style="outline"
                    aria-label={`Remove manual recipient ${email}`}
                    onClick={() =>
                      onManualRecipientsChange(
                        manualRecipients.filter((item) => item !== email),
                      )
                    }
                  >
                    <FaXmark aria-hidden="true" />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
            {!cdaUserListId && manualRecipients.length === 0 && (
              <TableRow>
                <TableCell colSpan={3} className="py-6 text-center">
                  <Text className="text-zinc-600">
                    No recipients added yet.
                  </Text>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {addMode && (
        <div className="grid gap-4 rounded-lg border border-blue-200 bg-blue-50 p-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="flex flex-wrap gap-2" aria-label="Recipient type">
              <Button
                type="button"
                color={addMode === "manual" ? "blue" : "light"}
                onClick={() => setAddMode("manual")}
              >
                Manual email
              </Button>
              <Button
                type="button"
                color={addMode === "user-list" ? "blue" : "light"}
                onClick={() => setAddMode("user-list")}
              >
                CDA user list
              </Button>
            </div>
            <Button
              type="button"
              color="light"
              aria-label="Close add recipient"
              onClick={() => {
                setAddMode(null);
                setManualError("");
              }}
            >
              <FaXmark aria-hidden="true" />
            </Button>
          </div>

          {addMode === "manual" ? (
            <div className="grid gap-2">
              <label
                htmlFor="manual-recipient-email"
                className="font-medium text-zinc-950"
              >
                Email address
              </label>
              <div className="flex flex-col gap-2 sm:flex-row">
                <Input
                  id="manual-recipient-email"
                  type="email"
                  value={manualEmail}
                  placeholder="name@example.mil"
                  aria-invalid={!!manualError}
                  onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
                    setManualEmail(event.target.value);
                    setManualError("");
                  }}
                  onKeyDown={(event: React.KeyboardEvent<HTMLInputElement>) => {
                    if (event.key === "Enter") {
                      event.preventDefault();
                      addManualRecipient();
                    }
                  }}
                />
                <Button type="button" onClick={addManualRecipient}>
                  Add email
                </Button>
              </div>
              {manualError && (
                <Text role="alert" className="text-red-700">
                  {manualError}
                </Text>
              )}
            </div>
          ) : (
            <div className="grid gap-2">
              <label
                htmlFor="cda-user-list-office"
                className="font-medium text-zinc-950"
              >
                User list office
              </label>
              <Dropdown
                id="cda-user-list-office"
                label="User list office"
                labelClassName="sr-only"
                value={userListOffice}
                onChange={(event: React.ChangeEvent<HTMLSelectElement>) => {
                  setUserListOffice(event.target.value);
                  setUserListSearch("");
                  setDebouncedUserListSearch("");
                }}
                options={orderedAvailableOffices.map((availableOffice) => (
                  <option key={availableOffice} value={availableOffice}>
                    {availableOffice}
                  </option>
                ))}
              />
              <label
                htmlFor="cda-user-list-search"
                className="font-medium text-zinc-950"
              >
                Find a CDA user list
              </label>
              <div className="-m-2 pr-4">
                <Search
                  id="cda-user-list-search"
                  value={userListSearch}
                  placeholder="Search list name or description"
                  onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
                    setUserListSearch(event.target.value)
                  }
                />
              </div>
              {cdaUserListId && (
                <Text className="text-sm text-zinc-600">
                  Choosing a different list replaces {cdaUserListId}.
                </Text>
              )}
              {userLists.isLoading ? (
                <Text role="status">Loading CDA user lists…</Text>
              ) : userLists.error ? (
                <Text role="alert" className="text-red-700">
                  {userLists.error.message}
                </Text>
              ) : filteredUserLists.length > 0 ? (
                <div className="max-h-52 overflow-auto rounded-lg border border-zinc-200 bg-white">
                  {filteredUserLists.map((list) => (
                    <button
                      key={list["user-list-id"]}
                      type="button"
                      className="flex w-full items-start justify-between gap-3 border-b border-zinc-100 px-4 py-3 text-left last:border-b-0 hover:bg-blue-50 focus:bg-blue-50"
                      onClick={() => chooseUserList(list["user-list-id"])}
                    >
                      <span>
                        <span className="block font-medium text-zinc-950">
                          {list["user-list-id"]}
                        </span>
                        {list.description && (
                          <span className="mt-1 block text-sm text-zinc-600">
                            {list.description}
                          </span>
                        )}
                      </span>
                      {list["user-list-id"] === cdaUserListId && (
                        <Badge color="blue">Selected</Badge>
                      )}
                    </button>
                  ))}
                </div>
              ) : (
                <Text>
                  {(userLists.data?.length ?? 0) === 0
                    ? `No CDA user lists exist for ${userListOffice}.`
                    : "No user lists match that search."}
                </Text>
              )}
              <Text>
                <a
                  className="font-medium text-blue-700 underline"
                  href={`${cdaUiRoot}/user-lists`}
                  target="_blank"
                  rel="noreferrer"
                >
                  Manage user lists in CDA
                </a>
              </Text>
            </div>
          )}
        </div>
      )}
    </section>
  );
};
